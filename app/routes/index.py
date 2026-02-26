"""首页路由模块"""
from flask import Blueprint, render_template

index_bp = Blueprint('index', __name__)


@index_bp.route('/')
def index():
    """首页路由
    
    Returns:
        html: 首页HTML
    """
    return render_template('index.html')
