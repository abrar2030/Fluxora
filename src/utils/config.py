import hydra
from omegaconf import DictConfig, OmegaConf

@hydra.main(config_path="../config", config_name="config")
def get_config(cfg: DictConfig) -> DictConfig:
    OmegaConf.set_struct(cfg, False)
    return cfg

def save_config(cfg: DictConfig, path: str):
    with open(path, "w") as f:
        OmegaConf.save(config=cfg, f=f)