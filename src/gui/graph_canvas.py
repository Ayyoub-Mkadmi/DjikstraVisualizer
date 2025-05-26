# graph_canvas.py

from PyQt5.QtWidgets import QWidget, QInputDialog
from PyQt5.QtGui import QPainter, QPen, QBrush, QFont, QColor, QPainterPath, QTransform, QCursor
from PyQt5.QtCore import Qt, QPointF, QTimer
from PyQt5.QtCore import QRectF

import math

class GraphCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []
        self.radius = 20
        self.edge_offset = 20
        self.curve_strength = 0.4

        self.dragging_node_index = None
        self.hover_node_index = None
        self.drag_offset = QPointF(0, 0)
        self.selected_node_for_edge = None
        self.eraser_mode = False
        self.allow_loops = True
        self.allow_duplicate_edges = True
        
        self.error_node_index = None
        self.error_timer = None

        self.setMouseTracking(True)
        self.setMinimumSize(800, 800)
        self.setStyleSheet("background-color: white;")

    def set_config(self, eraser_mode=False, allow_loops=True, allow_duplicate_edges=True):
        self.eraser_mode = eraser_mode
        self.allow_loops = allow_loops
        self.allow_duplicate_edges = allow_duplicate_edges
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.draw_edges(painter)
        self.draw_nodes(painter)
        self.draw_selected_edge_preview(painter)

    def draw_edges(self, painter):
        edge_groups = {}
        for src, dst, weight in self.edges:
            key = (src, dst) if src != dst else (src, dst, 'loop')
            edge_groups.setdefault(key, []).append((src, dst, weight))

        pen = QPen(QColor(60, 60, 60), 2)
        painter.setPen(pen)
        painter.setFont(QFont("Arial", 10))

        for key, edges in edge_groups.items():
            for i, (src, dst, weight) in enumerate(edges):
                if src >= len(self.nodes) or dst >= len(self.nodes):
                    continue
                x1, y1 = self.nodes[src]
                x2, y2 = self.nodes[dst]
                if src == dst:
                    self.draw_loop(painter, x1, y1, weight, i)
                else:
                    self.draw_curved_edge(painter, x1, y1, x2, y2, weight, i, len(edges))

    def draw_curved_edge(self, painter, x1, y1, x2, y2, weight, index, total):
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            return

        dx, dy = dx / length, dy / length
        perp_x, perp_y = -dy, dx
        offset = self.edge_offset * (index - (total - 1) / 2)

        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ctrl_x = mid_x + perp_x * offset * self.curve_strength
        ctrl_y = mid_y + perp_y * offset * self.curve_strength

        start_x = x1 + dx * self.radius
        start_y = y1 + dy * self.radius
        end_x = x2 - dx * self.radius
        end_y = y2 - dy * self.radius

        path = QPainterPath(QPointF(start_x, start_y))
        path.quadTo(ctrl_x, ctrl_y, end_x, end_y)
        painter.drawPath(path)

        angle = math.atan2(end_y - ctrl_y, end_x - ctrl_x)
        self.draw_arrow(painter, end_x, end_y, angle)

        # Offset label outward slightly and rotate it
        label_offset = 15 + (index * 10)
        label_x = ctrl_x + perp_x * label_offset
        label_y = ctrl_y + perp_y * label_offset

        self.draw_rotated_label(painter, str(weight), label_x, label_y, angle)

    def draw_loop(self, painter, x, y, weight, index):
        loop_radius = self.radius + 1 + index * 3  # Smaller and stacked spacing

        # Rectangle centered above the node
        rect = QRectF(x - loop_radius, y - 2.5 * loop_radius,
                    2 * loop_radius, 2 * loop_radius)

        path = QPainterPath()
        path.arcMoveTo(rect, 0)
        path.arcTo(rect, 0, 360)  # Draw a 270° arc

        painter.setPen(QPen(QColor(70, 70, 70), 2))
        painter.drawPath(path)

        # Draw weight label above the loop
        self.draw_label(painter, str(weight), x, y - 3 * loop_radius)

    def draw_arrow(self, painter, x, y, angle):
        size = 10
        painter.drawLine(int(x), int(y),
                         int(x - size * math.cos(angle - math.pi / 6)),
                         int(y - size * math.sin(angle - math.pi / 6)))
        painter.drawLine(int(x), int(y),
                         int(x - size * math.cos(angle + math.pi / 6)),
                         int(y - size * math.sin(angle + math.pi / 6)))

    def draw_label(self, painter, text, x, y):
        rect = painter.fontMetrics().boundingRect(text)
        rect.moveCenter(QPointF(x, y).toPoint())
        rect.adjust(-4, -2, 4, 2)
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(Qt.NoPen)
        painter.drawRect(rect)
        painter.setPen(QPen(Qt.black))
        painter.drawText(rect, Qt.AlignCenter, text)

    def draw_rotated_label(self, painter, text, x, y, angle):
        painter.save()
        painter.translate(x, y)
        painter.rotate(math.degrees(angle) % 360)
        painter.setPen(Qt.black)
        painter.setBrush(Qt.white)
        rect = painter.fontMetrics().boundingRect(text)
        rect.moveCenter(QPointF(0, 0).toPoint())
        rect.adjust(-4, -2, 4, 2)
        painter.drawRect(rect)
        painter.drawText(rect, Qt.AlignCenter, text)
        painter.restore()

    def draw_nodes(self, painter):
        for idx, (x, y) in enumerate(self.nodes):
            if idx == self.error_node_index:
                color = QColor(255, 100, 100)  # Red for error
                border = QColor(200, 0, 0)
            elif idx == self.selected_node_for_edge:
                color = QColor(180, 220, 255)
                border = QColor(50, 100, 180)
            else:
                color = QColor(200, 220, 255)
                border = QColor(50, 100, 180) if idx != self.hover_node_index else QColor(255, 120, 0)
                
            painter.setPen(QPen(border, 2))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(int(x - self.radius), int(y - self.radius), self.radius * 2, self.radius * 2)
            self.draw_label(painter, str(idx), x, y)

    def draw_selected_edge_preview(self, painter):
        if self.selected_node_for_edge is None or self.selected_node_for_edge >= len(self.nodes):
            return
        src = self.nodes[self.selected_node_for_edge]
        dst = self.mapFromGlobal(QCursor.pos())
        painter.setPen(QPen(Qt.DashLine))
        painter.drawLine(QPointF(*src), dst)

    def mousePressEvent(self, event):
        pos = event.pos()
        node_idx = self.get_node_at(pos.x(), pos.y())

        if self.eraser_mode:
            self.handle_eraser(pos.x(), pos.y(), node_idx)
            return

        if event.button() == Qt.LeftButton:
            if node_idx is not None:
                self.dragging_node_index = node_idx
                self.drag_offset = pos - QPointF(*self.nodes[node_idx])
            else:
                self.nodes.append((pos.x(), pos.y()))
                self.update()

        elif event.button() == Qt.RightButton:
            self.handle_right_click(node_idx)

        elif event.button() == Qt.MiddleButton:
            self.handle_eraser(pos.x(), pos.y(), node_idx)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self.dragging_node_index is not None:
            new_pos = pos - self.drag_offset
            self.nodes[self.dragging_node_index] = (new_pos.x(), new_pos.y())
            self.update()
        else:
            node_idx = self.get_node_at(pos.x(), pos.y())
            if node_idx != self.hover_node_index:
                self.hover_node_index = node_idx
                self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging_node_index = None

    def handle_right_click(self, node_idx):
        if node_idx is None:
            self.selected_node_for_edge = None
            self.update()
            return

        if self.selected_node_for_edge is None:
            self.selected_node_for_edge = node_idx
        else:
            src, dst = self.selected_node_for_edge, node_idx

            # Block loop if not allowed
            if not self.allow_loops and src == dst:
                self.show_error_feedback(src)
                self.selected_node_for_edge = None
                self.update()
                return

            # Block duplicates if not allowed
            if not self.allow_duplicate_edges and self.edge_exists(src, dst):
                self.show_error_feedback(src)
                self.selected_node_for_edge = None
                self.update()
                return

            # Passed all checks - prompt for weight and add edge
            weight, ok = QInputDialog.getInt(self, "Poids de l'arête", "Entrez le poids :", 1, 1, 999)
            if ok:
                self.edges.append((src, dst, weight))

            self.selected_node_for_edge = None

        self.update()

    def show_error_feedback(self, node_idx):
        self.error_node_index = node_idx
        self.update()
        
        # Reset the error after 1 second
        if self.error_timer:
            self.error_timer.stop()
        self.error_timer = QTimer.singleShot(1000, self.clear_error_feedback)

    def clear_error_feedback(self):
        self.error_node_index = None
        self.update()

    def edge_exists(self, src, dst):
        return any(e[0] == src and e[1] == dst for e in self.edges)

    def handle_eraser(self, x, y, node_idx):
        if node_idx is not None:
            self.delete_node(node_idx)
        else:
            self.delete_edge(x, y)

    def delete_node(self, idx):
        self.nodes.pop(idx)
        self.edges = [(u if u < idx else u - 1,
                       v if v < idx else v - 1,
                       w) for u, v, w in self.edges if u != idx and v != idx]
        if self.selected_node_for_edge == idx:
            self.selected_node_for_edge = None
        elif self.selected_node_for_edge is not None and self.selected_node_for_edge > idx:
            self.selected_node_for_edge -= 1
        self.update()

    def delete_edge(self, x, y):
        for i, (u, v, w) in enumerate(self.edges):
            if u >= len(self.nodes) or v >= len(self.nodes):
                continue
                
            x1, y1 = self.nodes[u]
            x2, y2 = self.nodes[v]
            
            if u == v:  # This is a loop edge
                loop_radius = self.radius + 1  # Base loop radius
                # Check if point is near the loop (approximate with a circle above the node)
                if math.hypot(x - x1, y - (y1 - 2 * loop_radius)) < loop_radius + 10:
                    self.edges.pop(i)
                    self.update()
                    return
            else:
                if self.is_point_near_edge(x, y, x1, y1, x2, y2):
                    self.edges.pop(i)
                    self.update()
                    return

    def get_node_at(self, x, y):
        for idx, (nx, ny) in enumerate(self.nodes):
            if (x - nx) ** 2 + (y - ny) ** 2 <= self.radius ** 2:
                return idx
        return None

    def is_point_near_edge(self, px, py, x1, y1, x2, y2, tolerance=10):
        steps = 20
        for i in range(steps + 1):
            t = i / steps
            x = (1 - t)**2 * x1 + 2 * (1 - t) * t * ((x1 + x2) / 2) + t**2 * x2
            y = (1 - t)**2 * y1 + 2 * (1 - t) * t * ((y1 + y2) / 2) + t**2 * y2
            if math.hypot(px - x, py - y) < tolerance:
                return True
        return False
    
    def export_graph(self):
        """Returns the graph edges in the format [(src, dst, weight), ...]"""
        # Sort edges for consistent output
        sorted_edges = sorted(self.edges, key=lambda x: (x[0], x[1], x[2]))
        return sorted_edges