import matplotlib.pyplot as plt
import numpy as np

from utils.agents import QSheep, QWolves
from utils.board import BaghChal


game_env = BaghChal(sheep_agent_cls=QSheep, wolves_agent_cls=QWolves)

history = {
    "rounds": [],
    "wolves": 0,
    "sheep": 0,
    "captured": [],
}
epochs = 1000
for epoch in range(1, epochs+1):
    _round = 1
    while True:
        # Sheep turn:
        new_state = game_env.sheep.make_turn(epoch,game_env.get_state())
        if new_state is None:
            game_env.sheep.update_q_from_trajectory(-1)
            # game_env.wolves.update_q_from_trajectory(1)
            history["wolves"] += 1
            break
        elif len(new_state) == 0:
            # all sheep are blocked
            game_env.sheep.update_q_from_trajectory(-1)
            # game_env.wolves.update_q_from_trajectory(-1)
            break
        else:
            game_env.step(new_state)

        # Wolves turn
        new_state = game_env.wolves.make_turn(game_env.get_state())
        if new_state is None:
            game_env.sheep.update_q_from_trajectory(1)
            # game_env.wolves.update_q_from_trajectory(-1)
            history["sheep"] += 1
            break 
        else:
            game_env.step(new_state)

    _round += 1
    history["captured"].append(game_env.wolves.captured_sheep)
    history["rounds"].append(_round)
    game_env.restart()
    if epoch % 1000 == 0:
        print(f"W: {history['wolves']}, S: {history['sheep']}, R : {epoch/1000}")
        history["wolves"] = 0
        history["sheep"] = 0
        # print(game_env.sheep.q_table)

# print(game_env.sheep.q_table)
# print(game_env.wolves.q_table)
game_env.wolves.save(path=r"C:\\Users\\dhung\\OneDrive\\Desktop\AIFinal\\AI-plays-Baagchal\\Qlearning", filename="q-wolves1")
game_env.sheep.save(path=r"C:\\Users\\dhung\\OneDrive\\Desktop\AIFinal\\AI-plays-Baagchal\\Qlearning", filename="q-sheep1")

# plot results:
fig, axs = plt.subplots(1, 2, figsize=(15, 7))
fig.suptitle(f"W: {history['wolves']}, S: {history['sheep']}")

axs[0].plot(history["rounds"], label='rounds/match')
axs[0].legend()
axs[1].plot(history["captured"], label="captured/match")
axs[1].legend()
plt.show()
