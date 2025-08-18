"""Agente DQN Avançado
Inclui:
 - Double DQN
 - Dueling Architecture (Value + Advantage)
 - Prioritized Experience Replay (proporcional simples)
 - Target Network sync periódico
 - Epsilon decay linear
 - Salvamento / carregamento do replay buffer
"""
from __future__ import annotations
import os
import json
import math
import numpy as np
from dataclasses import dataclass
from typing import Deque, Tuple, List, Optional
from collections import deque

import tensorflow as tf
from tensorflow.keras import layers, models, optimizers

# =============================
# Config
# =============================
@dataclass
class DQNConfig:
    state_size: int
    action_size: int
    gamma: float = 0.99
    lr: float = 1e-3
    epsilon_start: float = 1.0
    epsilon_end: float = 0.05
    epsilon_decay_steps: int = 10_000
    batch_size: int = 64
    buffer_size: int = 100_000
    min_buffer_size: int = 2_000
    target_sync_interval: int = 1_000
    train_interval: int = 4
    gradient_clip_norm: float = 5.0
    prioritized_alpha: float = 0.6
    prioritized_beta_start: float = 0.4
    prioritized_beta_steps: int = 50_000
    prioritized_eps: float = 1e-6
    save_path: str = "dqn_weights.h5"
    buffer_path: str = "replay_buffer.npz"
    dueling: bool = True
    double: bool = True

# =============================
# Prioritized Replay Buffer (proporcional)
# =============================
class PrioritizedReplayBuffer:
    def __init__(self, capacity: int, alpha: float, eps: float):
        self.capacity = capacity
        self.alpha = alpha
        self.eps = eps
        self.buffer: List[Tuple[np.ndarray,int,float,np.ndarray,bool]] = []
        self.priorities = np.zeros((capacity,), dtype=np.float32)
        self.pos = 0

    def add(self, s, a, r, s2, d, priority: Optional[float] = None):
        if len(self.buffer) < self.capacity:
            self.buffer.append((s,a,r,s2,d))
        else:
            self.buffer[self.pos] = (s,a,r,s2,d)
        if priority is None:
            max_prio = self.priorities.max() if self.buffer else 1.0
            self.priorities[self.pos] = max_prio if max_prio > 0 else 1.0
        else:
            self.priorities[self.pos] = priority
        self.pos = (self.pos + 1) % self.capacity

    def sample(self, batch_size: int, beta: float, eps: float):
        if len(self.buffer) == self.capacity:
            prios = self.priorities
        else:
            prios = self.priorities[:self.pos]
        probs = prios ** self.alpha
        probs /= probs.sum()
        indices = np.random.choice(len(self.buffer), batch_size, p=probs)
        samples = [self.buffer[i] for i in indices]
        total = len(self.buffer)
        weights = (total * probs[indices]) ** (-beta)
        weights /= weights.max()
        states, actions, rewards, next_states, dones = zip(*samples)
        return (np.array(states), np.array(actions), np.array(rewards, dtype=np.float32),
                np.array(next_states), np.array(dones, dtype=np.bool_), indices, weights.astype(np.float32))

    def update_priorities(self, indices, priorities):
        for idx, prio in zip(indices, priorities):
            self.priorities[idx] = prio

    def __len__(self):
        return len(self.buffer)

    def save(self, path: str):
        try:
            np.savez_compressed(path,
                                states=np.array([b[0] for b in self.buffer], dtype=np.float32),
                                actions=np.array([b[1] for b in self.buffer], dtype=np.int64),
                                rewards=np.array([b[2] for b in self.buffer], dtype=np.float32),
                                next_states=np.array([b[3] for b in self.buffer], dtype=np.float32),
                                dones=np.array([b[4] for b in self.buffer], dtype=np.bool_),
                                priorities=self.priorities,
                                pos=self.pos)
        except Exception:
            pass

    def load(self, path: str):
        if not os.path.isfile(path):
            return
        data = np.load(path, allow_pickle=True)
        size = len(data['actions'])
        self.buffer = []
        for i in range(size):
            self.buffer.append((data['states'][i], int(data['actions'][i]), float(data['rewards'][i]), data['next_states'][i], bool(data['dones'][i])))
        self.priorities[:size] = data['priorities'][:size]
        self.pos = int(data['pos']) if 'pos' in data else size % self.capacity

# =============================
# Network (Dueling opcional)
# =============================
class DQNAgent:
    def __init__(self, config: DQNConfig, seed: Optional[int] = None):
        self.cfg = config
        self.rng = np.random.default_rng(seed)
        tf.random.set_seed(seed or 42)
        self.epsilon = self.cfg.epsilon_start
        self.train_steps = 0
        self.env_steps = 0
        self.beta = self.cfg.prioritized_beta_start
        self.buffer = PrioritizedReplayBuffer(self.cfg.buffer_size, self.cfg.prioritized_alpha, self.cfg.prioritized_eps)
        self.model = self._build_network()
        self.target_model = self._build_network()
        self._sync_target(forced=True)
        # tenta carregar buffer existente
        self.buffer.load(self.cfg.buffer_path)

    def _build_network(self):
        inputs = layers.Input(shape=(self.cfg.state_size,), name='state')
        x = layers.Dense(256, activation='relu')(inputs)
        x = layers.Dense(256, activation='relu')(x)
        if self.cfg.dueling:
            adv = layers.Dense(128, activation='relu')(x)
            adv = layers.Dense(self.cfg.action_size, activation='linear')(adv)
            val = layers.Dense(128, activation='relu')(x)
            val = layers.Dense(1, activation='linear')(val)
            adv_mean = layers.Lambda(lambda a: tf.reduce_mean(a, axis=1, keepdims=True))(adv)
            q_out = layers.Add()([val, layers.Subtract()([adv, adv_mean])])
        else:
            q_out = layers.Dense(self.cfg.action_size, activation='linear')(x)
        model = models.Model(inputs, q_out)
        opt = optimizers.Adam(learning_rate=self.cfg.lr)
        model.compile(optimizer=opt, loss='mse')
        return model

    def _sync_target(self, forced: bool = False):
        self.target_model.set_weights(self.model.get_weights())
        self.last_sync_step = 0 if forced else self.train_steps

    def select_action(self, state: np.ndarray, greedy: bool = False) -> int:
        """Seleciona ação com epsilon-greedy e máscara de ações inválidas.
        Máscara: se não há posição (position_pct ~= 0) não permite SELL (ação 2).
        """
        # position_pct está no penúltimo índice do estado ([-2]) conforme TradingEnv
        position_pct = float(state[-2]) if len(state) >= 2 else 0.0
        if (not greedy) and (self.rng.random() < self.epsilon):
            # Escolha aleatória respeitando máscara
            if position_pct <= 1e-6:
                # não pode SELL
                return int(self.rng.integers(0, 2))  # 0 ou 1
            return int(self.rng.integers(0, self.cfg.action_size))
        q = self.model.predict(state[None, :], verbose=0)[0]
        if position_pct <= 1e-6:
            # força SELL a -inf para não ser escolhida
            q[2] = -1e12
        return int(np.argmax(q))

    def update_epsilon(self):
        frac = min(1.0, self.env_steps / self.cfg.epsilon_decay_steps)
        self.epsilon = self.cfg.epsilon_start + frac * (self.cfg.epsilon_end - self.cfg.epsilon_start)
        # beta para IS weights
        beta_frac = min(1.0, self.env_steps / self.cfg.prioritized_beta_steps)
        self.beta = self.cfg.prioritized_beta_start + beta_frac * (1.0 - self.cfg.prioritized_beta_start)

    def remember(self, s, a, r, s2, d):
        # prioridade inicial = max existente
        self.buffer.add(s, a, r, s2, d)

    def train_step(self):
        if len(self.buffer) < self.cfg.min_buffer_size:
            return None
        if self.env_steps % self.cfg.train_interval != 0:
            return None
        (states, actions, rewards, next_states, dones, idxs, weights) = self.buffer.sample(self.cfg.batch_size, self.beta, self.cfg.prioritized_eps)
        # Double DQN alvo
        if self.cfg.double:
            next_q_online = self.model.predict(next_states, verbose=0)
            next_actions = np.argmax(next_q_online, axis=1)
            next_q_target = self.target_model.predict(next_states, verbose=0)
            target_next = next_q_target[np.arange(self.cfg.batch_size), next_actions]
        else:
            target_next = np.max(self.target_model.predict(next_states, verbose=0), axis=1)
        targets_full = self.model.predict(states, verbose=0)
        td_errors = np.zeros(self.cfg.batch_size, dtype=np.float32)
        for i in range(self.cfg.batch_size):
            a = actions[i]
            if dones[i]:
                target = rewards[i]
            else:
                target = rewards[i] + self.cfg.gamma * target_next[i]
            td_errors[i] = target - targets_full[i, a]
            targets_full[i, a] = target
        # IS weights
        sample_weights = weights
        history = self.model.fit(states, targets_full, sample_weight=sample_weights, batch_size=self.cfg.batch_size, epochs=1, verbose=0)
        loss = float(history.history['loss'][0])
        # atualiza prioridades
        new_prios = np.abs(td_errors) + self.cfg.prioritized_eps
        self.buffer.update_priorities(idxs, new_prios)
        self.train_steps += 1
        if self.train_steps % self.cfg.target_sync_interval == 0:
            self._sync_target()
        return loss

    def save(self, path: Optional[str] = None):
        p = path or self.cfg.save_path
        self.model.save(p)
        # salva buffer
        self.buffer.save(self.cfg.buffer_path)
        meta = {"train_steps": self.train_steps, "env_steps": self.env_steps, "epsilon": self.epsilon}
        with open(p + '.meta.json', 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    def load(self, path: Optional[str] = None):
        p = path or self.cfg.save_path
        if not os.path.isfile(p):
            raise FileNotFoundError(p)
        self.model = models.load_model(p)
        self._sync_target(forced=True)
        meta_path = p + '.meta.json'
        if os.path.isfile(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            self.train_steps = meta.get('train_steps', 0)
            self.env_steps = meta.get('env_steps', 0)
            self.epsilon = meta.get('epsilon', self.epsilon)
        # carrega buffer
        self.buffer.load(self.cfg.buffer_path)

# Exemplo rápido de laço de treino integrando com TradingEnv
if __name__ == '__main__':
    from trading_env import TradingEnv, EnvConfig
    import pandas as pd

    # Dados sintéticos simples
    n = 800
    prices = pd.DataFrame({'close': np.linspace(100,130,n) + np.random.randn(n)})
    env = TradingEnv(prices, EnvConfig())

    cfg = DQNConfig(state_size=env.observation_space, action_size=env.action_space)
    agent = DQNAgent(cfg, seed=42)

    episodes = 2
    for ep in range(1, episodes+1):
        s = env.reset()
        done = False
        ep_reward = 0.0
        losses: List[float] = []
        while not done:
            a = agent.select_action(s)
            s2, r, done, info = env.step(a)
            agent.remember(s, a, r, s2, done)
            agent.env_steps += 1
            agent.update_epsilon()
            loss = agent.train_step()
            if loss is not None:
                losses.append(loss)
            s = s2
            ep_reward += r
        print(f"Ep {ep} Reward {ep_reward:.4f} LossAvg {np.mean(losses) if losses else 0:.5f} Eps {agent.epsilon:.3f}")
    agent.save()
