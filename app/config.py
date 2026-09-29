"""CP1 — Cấu hình theo 12-Factor.

Giá trị không nhạy cảm có mặc định và có thể được ghi đè bằng biến môi trường.
Secret phải được cung cấp qua môi trường để cùng một image chạy ở laptop,
staging và production mà không phải sửa code.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Toàn bộ cấu hình của service.

    pydantic-settings tự đọc biến môi trường theo tên trường (không phân biệt
    hoa thường), nên ``agent_api_key`` lấy giá trị từ ``AGENT_API_KEY``.

    | Trường                  | Kiểu  | Mặc định                   |
    |-------------------------|-------|----------------------------|
    | port                    | int   | 8000                       |
    | agent_api_key           | str   | KHÔNG có mặc định (bắt buộc)|
    | redis_url               | str   | "redis://localhost:6379/0" |
    | rate_limit_per_minute   | int   | 10                         |
    | monthly_budget_usd      | float | 10.0                       |
    | log_level               | str   | "INFO"                     |

    ``agent_api_key`` không có mặc định để ứng dụng dừng ngay khi thiếu secret.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    port: int = 8000
    agent_api_key: str = Field(min_length=1)
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_per_minute: int = 10
    monthly_budget_usd: float = 10.0
    log_level: str = "INFO"

    @field_validator("agent_api_key")
    @classmethod
    def reject_blank_api_key(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("AGENT_API_KEY must not be blank")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Đọc cấu hình một lần rồi cache lại (đọc env mỗi request là lãng phí)."""
    return Settings()
