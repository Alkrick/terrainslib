import hydra
from omegaconf import DictConfig

from terrainslib.visualize import plot_heightmap, plot_3d_surface, draw_mesh
from terrainslib.generators.registry import REGISTRY


@hydra.main(config_path="configs", config_name="config", version_base=None)
def main(cfg: DictConfig):
    for name, cls in REGISTRY.items():
        print(f"testing: {name}")
        
        cfg = cls()
        cfg.convert()
        terrain = cfg.generate(0.5)
        
        plot_heightmap(terrain)
    
    


if __name__ == "__main__":
    main()
