"""create notifications table

Revision ID: 001
Revises: 
Create Date: 2024-03-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create notification type enum
    notification_type = postgresql.ENUM(
        'system',
        'security',
        'user',
        'support',
        'marketplace',
        'deployment',
        name='notificationtype'
    )
    notification_type.create(op.get_bind())

    # Create notification priority enum
    notification_priority = postgresql.ENUM(
        'low',
        'medium',
        'high',
        'urgent',
        name='notificationpriority'
    )
    notification_priority.create(op.get_bind())

    # Create notification status enum
    notification_status = postgresql.ENUM(
        'unread',
        'read',
        'archived',
        'deleted',
        name='notificationstatus'
    )
    notification_status.create(op.get_bind())

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', notification_type, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.String(length=5000), nullable=False),
        sa.Column('priority', notification_priority, nullable=False),
        sa.Column('status', notification_status, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('action_url', sa.String(length=512), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create notification preferences table
    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', notification_type, nullable=False),
        sa.Column('email_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('push_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('in_app_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(
        'ix_notifications_user_id',
        'notifications',
        ['user_id']
    )
    op.create_index(
        'ix_notifications_status',
        'notifications',
        ['status']
    )
    op.create_index(
        'ix_notifications_created_at',
        'notifications',
        ['created_at']
    )
    op.create_index(
        'ix_notification_preferences_user_id',
        'notification_preferences',
        ['user_id']
    )
    op.create_index(
        'ix_notification_preferences_type',
        'notification_preferences',
        ['type']
    )

def downgrade():
    # Drop indexes
    op.drop_index('ix_notifications_user_id')
    op.drop_index('ix_notifications_status')
    op.drop_index('ix_notifications_created_at')
    op.drop_index('ix_notification_preferences_user_id')
    op.drop_index('ix_notification_preferences_type')

    # Drop tables
    op.drop_table('notification_preferences')
    op.drop_table('notifications')

    # Drop enums
    notification_type = postgresql.ENUM(
        'system',
        'security',
        'user',
        'support',
        'marketplace',
        'deployment',
        name='notificationtype'
    )
    notification_type.drop(op.get_bind())

    notification_priority = postgresql.ENUM(
        'low',
        'medium',
        'high',
        'urgent',
        name='notificationpriority'
    )
    notification_priority.drop(op.get_bind())

    notification_status = postgresql.ENUM(
        'unread',
        'read',
        'archived',
        'deleted',
        name='notificationstatus'
    )
    notification_status.drop(op.get_bind()) 