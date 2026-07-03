import hydra
from omegaconf import DictConfig


from terrainslib.api import create_terrain
from terrainslib.visualize import plot_heightmap, plot_3d_surface, draw_mesh



@hydra.main(config_path="configs", config_name="config", version_base=None)
def main(cfg: DictConfig):

    
    terrain = create_terrain(cfg)
    
    print(terrain.metadata)
    plot_heightmap(terrain)
    draw_mesh(terrain)
    # plot_3d_surface(terrain)


if __name__ == "__main__":
    main()
