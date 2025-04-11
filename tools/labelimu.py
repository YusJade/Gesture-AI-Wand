import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint
from OpenGL.GL import *
from OpenGL.GLU import *


class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_pos = QPoint(0, 0)
        self.rot_x = 0  # X轴旋转角度
        self.rot_y = 0  # Y轴旋转角度
        self.scale = 1  # 缩放比例

        # 生成不规则轨迹的点（示例：螺旋线 + 随机扰动）
        self.trajectory = self.generate_trajectory()

    def generate_trajectory(self, num_points=500):
        """生成3D不规则轨迹（螺旋线 + 随机噪声）"""
        t = np.linspace(0, 8 * np.pi, num_points)  # 参数t
        x = np.sin(t) * (1 + 0.1 * np.random.randn(num_points))  # X轴：正弦波 + 噪声
        y = np.cos(t) * (1 + 0.1 * np.random.randn(num_points))  # Y轴：余弦波 + 噪声
        z = t / 10  # Z轴：线性增长
        return np.column_stack((x, y, z))  # 合并为Nx3数组

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)  # 黑色背景
        glEnable(GL_DEPTH_TEST)  # 启用深度测试
        glEnable(GL_LINE_SMOOTH)  # 启用线条抗锯齿

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # 设置透视投影
        gluPerspective(45, self.width() / self.height(), 0.1, 100.0)
        gluLookAt(0, 0, 10, 0, 0, 0, 0, 1, 0)  # 摄像机位置

        # 应用旋转和缩放
        glRotatef(self.rot_x, 1, 0, 0)  # 绕 X 轴旋转
        glRotatef(self.rot_y, 0, 1, 0)  # 绕 Y 轴旋转
        glScalef(self.scale, self.scale, self.scale)  # 缩放

        # 绘制轨迹线
        glBegin(GL_LINE_STRIP)
        glColor3f(0.0, 1.0, 0.0)  # 绿色轨迹
        for point in self.trajectory:
            glVertex3fv(point)
        glEnd()

        # 在轨迹末端绘制一个红色小球标记当前位置
        glPushMatrix()
        glTranslatef(*self.trajectory[-1])  # 移动到最后一个点
        glColor3f(1.0, 0.0, 0.0)  # 红色
        quadric = gluNewQuadric()
        gluSphere(quadric, 0.1, 16, 16)  # 绘制小球
        gluDeleteQuadric(quadric)
        glPopMatrix()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()
            self.rot_y += dx * 0.5  # 水平拖拽 -> 绕 Y 轴旋转
            self.rot_x -= dy * 0.5  # 垂直拖拽 -> 绕 X 轴旋转
            self.last_pos = event.pos()
            self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale *= 1.1  # 放大
        else:
            self.scale *= 0.9  # 缩小
        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = GLWidget()
    widget.resize(800, 600)
    widget.setWindowTitle("3D 不规则运动轨迹（支持拖拽视角）")
    widget.show()
    sys.exit(app.exec_())
