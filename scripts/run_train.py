import sys, os
sys.path.append(os.path.abspath('.')) import argparse
from src.game.pokemon_platinum_env import PokemonPlatinumEnv
from src.rl.train import train def main():
p = argparse.ArgumentParser()
p.add_argument("--melonds-exe", required=True)
p.add_argument("--rom", required=True)
p.add_argument("--keymap", default="configs/keymap_windows.json")
p.add_argument("--rewards-config", default="configs/rewards_pokemon_platinum.json")
p.add_argument("--episodes", type=int, default=50)
p.add_argument("--eval-every", type=int, default=10)
p.add_argument("--frame-skip", type=int, default=4)
p.add_argument("--stack-frames", type=int, default=4)
args = p.parse_args()
env = PokemonPlatinumEnv(
    melonds_exe=args.melonds_exe,
    rom_path=args.rom,
    keymap_path=args.keymap,
    rewards_config_path=args.rewards_config,
    frame_skip=args.frame_skip,
    stack_frames=args.stack_frames,
    focus_each_step=True,
)
train(env, episodes=args.episodes, eval_every=args.eval_every)