import hydra
from omegaconf import DictConfig
from terrainslib.common.roughness import apply_roughness, RoughnessConfig
from terrainslib.generators.registry import REGISTRY
from terrainslib.visualize import plot_heightmap, plot_3d_surface, draw_mesh


def build_terrain(cfg):

    terrain_type = cfg.terrain.type

    if terrain_type not in REGISTRY:
        raise ValueError(
            f"Unknown terrain type '{terrain_type}'. "
            f"Available: {list(REGISTRY.keys())}"
        )

    func = REGISTRY[terrain_type]

    kwargs = dict(cfg.terrain)
    kwargs.pop("type", None)
    
    
    roughness_cfg = kwargs.pop("roughness")
    
    print(roughness_cfg)
    terrain = func(**kwargs)
    terrain = apply_roughness(
        terrain,
        RoughnessConfig(
            enabled=roughness_cfg.enabled,
            amplitude=roughness_cfg.amplitude,
            seed=cfg.seed,
        ),
    )

    return terrain


@hydra.main(config_path="configs", config_name="config", version_base=None)
def main(cfg: DictConfig):

    terrain = build_terrain(cfg)

    
    print(terrain.metadata)
    plot_heightmap(terrain)
    draw_mesh(terrain)
    # plot_3d_surface(terrain)


if __name__ == "__main__":
    main()
