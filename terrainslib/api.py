
from omegaconf import OmegaConf
from terrainslib.generators.registry import REGISTRY



def create_terrain(user_cfg):
    
    terrain = user_cfg.terrain.name

    if terrain not in REGISTRY:
        raise ValueError(
            f"Unknown terrain name '{terrain}'. "
            f"Available: {list(REGISTRY.keys())}"
        )

    terrain_cls = REGISTRY[terrain]
    default_cfg = OmegaConf.structured(terrain_cls())
    
    # STEP 1: resolve ALL interpolations in full scope    
    OmegaConf.resolve(user_cfg)
    
    # STEP 2: merge just terrain (after resolution we have eveything we need here)
    merged = OmegaConf.merge(default_cfg, user_cfg.terrain)
    
    terrain_cfg = OmegaConf.to_object(merged)    
    # terrain_cfg.convert()
    print(terrain_cfg)
    return terrain_cfg.generate(1.0)