"""initial unicrypt schema

Revision ID: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("username", sa.String(80), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", sa.String(20), nullable=False),
        sa.Column("department", sa.String(120), nullable=False), sa.Column("profile_image", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True)), sa.Column("is_online", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_table("conversations",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("professor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_conversations_student_id", "conversations", ["student_id"])
    op.create_index("ix_conversations_professor_id", "conversations", ["professor_id"])
    op.create_table("messages",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("encrypted_content", sa.Text(), nullable=False),
        sa.Column("nonce", sa.String(255), nullable=False), sa.Column("authentication_tag", sa.String(255), nullable=False),
        sa.Column("algorithm", sa.String(40), nullable=False), sa.Column("message_type", sa.String(20), nullable=False),
        sa.Column("delivery_status", sa.String(20), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])
    op.create_index("ix_messages_sender_id", "messages", ["sender_id"])
    op.create_table("voice_messages",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("encrypted_file_path", sa.String(500), nullable=False),
        sa.Column("nonce", sa.String(255), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_voice_messages_conversation_id", "voice_messages", ["conversation_id"])
    op.create_index("ix_voice_messages_sender_id", "voice_messages", ["sender_id"])
    op.create_table("encryption_keys",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("peer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("public_key", sa.Text()),
        sa.Column("encrypted_key_material", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_encryption_keys_owner_id", "encryption_keys", ["owner_id"])
    op.create_index("ix_encryption_keys_peer_id", "encryption_keys", ["peer_id"])


def downgrade():
    op.drop_table("encryption_keys"); op.drop_table("voice_messages"); op.drop_table("messages"); op.drop_table("conversations"); op.drop_index("ix_users_username", table_name="users"); op.drop_table("users")
