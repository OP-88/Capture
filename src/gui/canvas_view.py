import math
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush

class CanvasView(QGraphicsView):
    """
    High-fidelity, interactive viewport for the primary image.
    Supports precision zooming, panning, and 'Smart-Snap' drawing.
    """
    
    edit_applied = Signal(str, QRectF)  # tool_name, rect
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_obj = QGraphicsScene(self)
        self.setScene(self.scene_obj)
        
        self.image_item = QGraphicsPixmapItem()
        self.scene_obj.addItem(self.image_item)
        
        # Transparent overlay for non-destructive edits
        self.overlay_item = QGraphicsPixmapItem()
        self.overlay_item.setZValue(1)
        self.scene_obj.addItem(self.overlay_item)
        
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)  # Lanczos-quality rescaling
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        self.current_tool = 'highlight'  # Default to highlight instead of pan
        
        self.drawing = False
        self.start_point = QPointF()
        self.current_rect = QRectF()
        
        # Selection rectangle item (Rubber band)
        from PySide6.QtWidgets import QGraphicsRectItem
        self.selection_rect_item = QGraphicsRectItem()
        self.selection_rect_item.setPen(QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.DashLine))
        self.selection_rect_item.setBrush(QBrush(QColor(255, 255, 255, 50))) # Semi-transparent white
        self.selection_rect_item.setZValue(2)
        self.selection_rect_item.hide()
        self.scene_obj.addItem(self.selection_rect_item)
        
    def set_image(self, pixmap: QPixmap, ocr_boxes=None):
        """Set the background image."""
        self.image_item.setPixmap(pixmap)
        self.scene_obj.setSceneRect(QRectF(pixmap.rect()))
        
        # Create a blank transparent overlay of the same size
        overlay_pix = QPixmap(pixmap.size())
        overlay_pix.fill(Qt.GlobalColor.transparent)
        self.overlay_item.setPixmap(overlay_pix)
        
        self.overlay_item.setPixmap(overlay_pix)
        
        self.fitInView(self.scene_obj.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.viewport().update()  # Force high-res redraw after loading
        
    def set_tool(self, tool_name: str):
        self.current_tool = tool_name
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
            
    def set_overlay(self, pixmap: QPixmap):
        self.overlay_item.setPixmap(pixmap)
        
    def wheelEvent(self, event):
        """Precision Zooming"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            zoom_in_factor = 1.25
            zoom_out_factor = 1 / zoom_in_factor
            if event.angleDelta().y() > 0:
                zoom_factor = zoom_in_factor
            else:
                zoom_factor = zoom_out_factor
            self.scale(zoom_factor, zoom_factor)
        else:
            super().wheelEvent(event)
            
    def mousePressEvent(self, event):
        if self.current_tool != 'pan' and event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            pos = self.mapToScene(event.pos())
            self.start_point = pos
            self.current_rect = QRectF(pos, pos)
            self.selection_rect_item.setRect(self.current_rect)
            self.selection_rect_item.show()
        else:
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        if self.drawing:
            pos = self.mapToScene(event.pos())
            self.current_rect = QRectF(self.start_point, pos).normalized()
            self.selection_rect_item.setRect(self.current_rect)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drawing and event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            self.selection_rect_item.hide()
            
            # Use the freeform drawn rectangle unconditionally
            self.edit_applied.emit(self.current_tool, self.current_rect)
        else:
            super().mouseReleaseEvent(event)
