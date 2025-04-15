# File: fieldShape
# Author: Haozhou Wang
# Organization: UTOkyo FieldPhenomics Lab
# Description:
#     Creating subplots inside the given plot boundary
# Dependencies:
#     - Python 3.x
#     - QGIS 3.x
# License: MIT
# Usage: run script directly in python console of QGIS

from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                QLineEdit, QPushButton, QComboBox, QCheckBox,
                                QMessageBox, QFileDialog)
from qgis.PyQt.QtCore import (Qt, QVariant, QLocale)
from qgis.PyQt import QtGui
from qgis.core import (QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, 
                      QgsRectangle, QgsWkbTypes, QgsCoordinateReferenceSystem,
                      QgsCoordinateTransform, QgsField, QgsFields, 
                      QgsVector, QgsPointXY, QgsVectorFileWriter,
                      QgsMapLayer, QgsFillSymbol)
from qgis.gui import QgsMapCanvas
from qgis.utils import iface

import math
import os
import tempfile

i18n_en = {
    "windowTitle": "Subplot Division Tool",
    "layerLbl": "Select plot boundary polygon layer:",
    "focusBtn": "Focus",
    "colsLbl": "Horizontal divisions (columns):",
    "rowsLbl": "Vertical divisions (rows):",
    "domLbl": "Select DOM layer (for output CRS):",
    "xBufLbl": "Row spacing (m), negative for overlap:",
    "yBufLbl": "Column spacing (m), negative for overlap:",
    "outputLbl": "Output file path:",
    "outputPlacehold": "Save as temporary file",
    "runBtn": "Execute",
    "prevWinTitle": "Division Preview",

    "savefileDialogTitle": "Save Output File",
    "savefileDialogTypes": "Shapefiles (*.shp);;All files (*)",

    "err": "Error",
    "errNotAPolygon": "Please select a valid polygon layer!",
    "errNotOneLayer": "Plot boundary layer must contain exactly one feature!",
    "errNotGoodPoly": "Invalid polygon geometry!",
    "errNot4Poly": "Polygon must be a quadrilateral (4 vertices)!",
    "errNoZero": "Rows and columns must be greater than 0!",
    "errException": "Input validation failed",
    "errRot": "Cannot calculate rotation angle!",
    "errNegative": "Buffer value too large - resulting subplot size is negative",
    "errMinRect": "Cannot calculate minimum bounding rectangle!",
    "errPrevRange": "Cannot calculate valid preview range!",
    "errMeterCRS": "Please select a projected CRS with meter units",
    "errSave": "Failed to save file:",
    "errSaveLoad": "Cannot load saved layer!",

    "success": "Success",
    "sucSave": "Subplots successfully created and saved to",
    "sucSaveTemp": "Subplots successfully created as temporary layer"
}

i18n_cn = {
    "windowTitle": "样地分割工具",
    "layerLbl": "选择样地边界多边形图层:",
    "focusBtn": "聚焦",
    "colsLbl": "水平分割份数(行数):",
    "rowsLbl": "垂直分割份数(列数):",
    "domLbl": "选择DOM图层(用于输出CRS)",
    "xBufLbl": "行间距(米), 负值表示互相重叠: ",
    "yBufLbl": "列间距(米), 负值表示互相重叠: ",
    "outputLbl": "输出文件路径:",
    "outputPlacehold": "储存为临时文件",
    "runBtn": "运行",
    "prevWinTitle": "分割预览",

    "savefileDialogTitle": "保存输出文件",
    "savefileDialogTypes": "Shapefiles (*.shp);;所有文件 (*)",

    "err": "错误",
    "errNotAPolygon": "请选择一个有效的多边形图层!",
    "errNotOneLayer": "样地边界图层应只包含一个要素!",
    "errNotGoodPoly": "多边形几何无效!",
    "errNot4Poly": "多边形应为一个四边形(4个顶点)!",
    "errNoZero": "行数和列数必须大于0!",
    "errException": "输入验证失败",
    "errRot": "无法计算旋转角度!",
    "errNegative": "缓冲区值过大导致子地块尺寸为负值",
    "errMinRect": "无法计算最小面积外接矩形!",
    "errPrevRange":  "无法计算有效的预览范围!",
    "errMeterCRS": "请选择米制单位的投影坐标系",
    "errSave": "保存文件失败:",
    "errSaveLoad": "无法加载保存的图层!",

    "success": "成功",
    "sucSave": "子区域已成功创建并保存到",
    "sucSaveTemp": "子区域已成功创建为临时图层"
}

i18n_jp = {
    "windowTitle": "プロット分割ツール",
    "layerLbl": "プロット境界ポリゴンレイヤを選択:",
    "focusBtn": "フォーカス",
    "colsLbl": "水平分割数(列数):",
    "rowsLbl": "垂直分割数(行数):",
    "domLbl": "DOMレイヤを選択(出力CRS用):",
    "xBufLbl": "行間隔(m), 負値は重なりを意味:",
    "yBufLbl": "列間隔(m), 負値は重なりを意味:",
    "outputLbl": "出力ファイルパス:",
    "outputPlacehold": "一時ファイルとして保存",
    "runBtn": "実行",
    "prevWinTitle": "分割プレビュー",

    "savefileDialogTitle": "出力ファイルを保存",
    "savefileDialogTypes": "シェープファイル (*.shp);;すべてのファイル (*)",

    "err": "エラー",
    "errNotAPolygon": "有効なポリゴンレイヤを選択してください!",
    "errNotOneLayer": "プロット境界レイヤは1つのみ含む必要あり!",
    "errNotGoodPoly": "無効なポリゴン形状です!",
    "errNot4Poly": "ポリゴンは四角形(4頂点)である必要あり!",
    "errNoZero": "行数と列数は0より大きい必要あり!",
    "errException": "入力検証失敗",
    "errRot": "回転角度を計算できません!",
    "errNegative": "バッファ値が大きすぎてサブプロットサイズが負に",
    "errMinRect": "最小外接矩形を計算できません!",
    "errPrevRange": "有効なプレビュー範囲を計算できません!",
    "errMeterCRS": "メートル単位の投影座標系を選択してください",
    "errSave": "ファイル保存失敗:",
    "errSaveLoad": "保存したレイヤを読み込めません!",

    "success": "成功",
    "sucSave": "サブプロットの作成と保存に成功:",
    "sucSaveTemp": "サブプロットが一時レイヤとして作成されました"
}

locale = QLocale.system().name()
lang = i18n_cn if locale.startswith("zh") else i18n_jp if locale.startswith("ja") else i18n_en

class SubplotDivisionDialog(QDialog):

    """
    无视样地在地里面的朝向，仅按长短边来进行判断

    O------>  col
    |
    |
    v  row

           long edge (width, x)
    +---------------------------+
    |                           |
    |                           |  short edge (height, y)
    |                           |
    +---------------------------+

      +--+   +--+   +--+   +--+
      |  |   |  |   |  |   |  |     
      |  |   |  |   |  |   |  |     
      |  |   |  |   |  |   |  |     
      +--+   +--+   +--+   +--+     
    ^      
    |  y_buffer
    v
      +--+   +--+   +--+   +--+
      |  |   |  |   |  |   |  |
      |  |   |  |   |  |   |  |
      |  |   |  |   |  |   |  |
      +--+   +--+   +--+   +--+
          <->    <->    <->    
               x_buffer 
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(lang['windowTitle'])
        self.setMinimumWidth(400)
        
        # 创建UI元素
        layout = QVBoxLayout()

        self.layer_label = QLabel(lang['layerLbl'])
        self.layer_combo = QComboBox()
        self.populate_layer_combo()
        
        # 选择输入图层
        layer_controls = QHBoxLayout()
        layer_controls.addWidget(self.layer_combo, 5)

        # 新增聚焦按钮
        self.focus_button = QPushButton(lang['focusBtn'])
        self.focus_button.clicked.connect(self.focus_and_rotate)
        layer_controls.addWidget(self.focus_button)

        layout.addWidget(self.layer_label, 1)
        layout.addLayout(layer_controls)
        
        # 行数和列数
        self.cols_label = QLabel(lang['colsLbl'])
        self.cols_edit = QLineEdit("5")
        self.cols_edit.setValidator(QtGui.QIntValidator(1, 100))
        layout.addWidget(self.cols_label)
        layout.addWidget(self.cols_edit)

        self.rows_label = QLabel(lang['rowsLbl'])
        self.rows_edit = QLineEdit("5")
        self.rows_edit.setValidator(QtGui.QIntValidator(1, 100))
        layout.addWidget(self.rows_label)
        layout.addWidget(self.rows_edit)
        
        # 选择DOM图层用于CRS
        self.dom_label = QLabel(lang['domLbl'])
        self.dom_combo = QComboBox()
        self.populate_dom_combo()
        layout.addWidget(self.dom_label)
        layout.addWidget(self.dom_combo)
        
        # 缓冲区设置
        self.x_buffer_label = QLabel(lang['xBufLbl'])
        self.x_buffer_edit = QLineEdit("0")
        # self.x_buffer_edit.setToolTip("AAA")
        self.x_buffer_edit.setValidator(QtGui.QDoubleValidator())
        layout.addWidget(self.x_buffer_label)
        layout.addWidget(self.x_buffer_edit)
        
        self.y_buffer_label = QLabel(lang['yBufLbl'])
        self.y_buffer_edit = QLineEdit("0")
        self.y_buffer_edit.setValidator(QtGui.QDoubleValidator())
        layout.addWidget(self.y_buffer_label)
        layout.addWidget(self.y_buffer_edit)
        
        # 输出选项
        self.output_label = QLabel(lang['outputLbl'])
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText(lang["outputPlacehold"])  # 灰色提示文字
        self.output_button = QPushButton("...")  # 改为单个点按钮
        self.output_button.setFixedWidth(30)  # 实际使用30px，10px会太窄无法正常显示
        self.output_button.clicked.connect(self.select_output)

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(self.output_button)
        layout.addWidget(self.output_label)
        layout.addLayout(output_layout)
        
        # 按钮
        # self.preview_button = QPushButton("Preview")
        # self.preview_button.clicked.connect(self.preview)
        self.run_button = QPushButton(lang['runBtn'])
        self.run_button.clicked.connect(self.run)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout = QHBoxLayout()
        # button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 预览画布
        self.preview_canvas = None

        # 添加旋转角度存储变量
        self.rotation_angle = 0.0
    
    def populate_layer_combo(self):
        """填充多边形图层到下拉框"""
        self.layer_combo.clear()
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                self.layer_combo.addItem(layer.name(), layer)
    
    def populate_dom_combo(self):
        """填充DOM图层到下拉框"""
        self.dom_combo.clear()
        self.dom_combo.addItem("", None)
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            self.dom_combo.addItem(layer.name(), layer)
    
    def toggle_output(self, state):
        """切换输出文件路径的可用状态"""
        self.output_edit.setEnabled(state)
        self.output_button.setEnabled(state)
    
    def select_output(self):
        """选择输出文件路径"""
        path, _ = QFileDialog.getSaveFileName(
            self, lang["savefileDialogTitle"], "", lang["savefileDialogTypes"]
        )
        if path:
            if not path.lower().endswith('.shp'):
                path += '.shp'
            self.output_edit.setText(path)
    
    def validate_input(self, geometry_only=False):
        """验证输入参数"""
        try:
            # 检查图层
            layer = self.layer_combo.currentData()
            if not layer or layer.featureCount() == 0:
                QMessageBox.warning(self, lang["err"], lang["errNotAPolygon"])
                return False
            
            if layer.featureCount() > 1:
                QMessageBox.warning(self, lang["err"], lang["errNotOneLayer"])
                return False
            
            feature = next(layer.getFeatures())
            geom = feature.geometry()
            
            # 检查顶点数
            if not geom.isGeosValid():
                QMessageBox.warning(self, lang["err"], lang["errNotGoodPoly"])
                return False
            
            # 如果是仅验证几何，直接返回
            if geometry_only:
                return True
            
            # 获取顶点数
            vertices = []
            if geom.isMultipart():
                for part in geom.asGeometryCollection():
                    vertices.extend(part.asPolygon()[0])
            else:
                vertices = geom.asPolygon()[0]
            
            if len(vertices) != 5:  # 注意:闭合多边形第一个和最后一个顶点相同
                QMessageBox.warning(self, lang["err"], lang["errNot4Poly"])
                return False
            
            # 检查行数和列数
            rows = int(self.rows_edit.text())
            cols = int(self.cols_edit.text())
            if rows <= 0 or cols <= 0:
                QMessageBox.warning(self, lang["err"], lang["errNoZero"])
                return False
            
            return True
            
        except Exception as e:
            QMessageBox.warning(self, lang["err"], f"{lang['errException']}: {str(e)}")
            return False
    
    def get_min_area_rectangle(self, polygon):
        """获取多边形的最小面积外接矩形"""
        # 获取多边形的凸包
        convex_hull = polygon.convexHull()
        
        # 获取顶点
        vertices = []
        if convex_hull.isMultipart():
            for part in convex_hull.asGeometryCollection():
                vertices.extend(part.asPolygon()[0])
        else:
            vertices = convex_hull.asPolygon()[0]
        
        # 移除重复的最后一个顶点(闭合多边形)
        if vertices[0] == vertices[-1]:
            vertices = vertices[:-1]
        
        min_area = float('inf')
        best_rect = None
        
        # 尝试所有可能的边作为矩形的边
        for i in range(len(vertices)):
            # 当前边作为矩形的一条边
            p1 = vertices[i]
            p2 = vertices[(i+1)%len(vertices)]
            
            # 计算边的角度
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            angle = math.atan2(dy, dx)
            
            # 旋转多边形使边水平
            rotated_vertices = []
            cos_ang = math.cos(-angle)
            sin_ang = math.sin(-angle)
            
            for p in vertices:
                # 平移使p1在原点
                tx = p.x() - p1.x()
                ty = p.y() - p1.y()
                # 旋转
                rx = tx * cos_ang - ty * sin_ang
                ry = tx * sin_ang + ty * cos_ang
                rotated_vertices.append((rx, ry))
            
            # 计算旋转后的边界框
            min_x = min(v[0] for v in rotated_vertices)
            max_x = max(v[0] for v in rotated_vertices)
            min_y = min(v[1] for v in rotated_vertices)
            max_y = max(v[1] for v in rotated_vertices)
            
            # 计算面积
            area = (max_x - min_x) * (max_y - min_y)
            
            # 检查是否是最小面积
            if area < min_area:
                min_area = area
                
                # 创建矩形顶点
                rect_vertices = [
                    (min_x, min_y),
                    (max_x, min_y),
                    (max_x, max_y),
                    (min_x, max_y)
                ]
                
                # 逆旋转矩形顶点
                unrotated_vertices = []
                cos_ang = math.cos(angle)
                sin_ang = math.sin(angle)
                
                for v in rect_vertices:
                    # 旋转
                    rx = v[0] * cos_ang - v[1] * sin_ang
                    ry = v[0] * sin_ang + v[1] * cos_ang
                    # 平移回原位置
                    tx = rx + p1.x()
                    ty = ry + p1.y()
                    unrotated_vertices.append(QgsPointXY(tx, ty))
                
                # 创建矩形几何
                best_rect = QgsGeometry.fromPolygonXY([unrotated_vertices])

        return best_rect
    
    def calculate_rotation_angle(self):
        """计算将边界框长边转为水平所需的旋转角度"""
        if not self.validate_input(geometry_only=True):
            return None
        
        layer = self.layer_combo.currentData()
        feature = next(layer.getFeatures())
        geom = feature.geometry()
        
        # 获取最小面积外接矩形
        rect_geom = self.get_min_area_rectangle(geom)
        if not rect_geom:
            return None
        
        # 获取矩形顶点
        vertices = rect_geom.asPolygon()[0][:-1]  # 移除闭合顶点
        
        # 计算长边和短边
        bottom_vec = QgsVector(vertices[1].x() - vertices[0].x(),
                            vertices[1].y() - vertices[0].y())
        left_vec = QgsVector(vertices[3].x() - vertices[0].x(),
                        vertices[3].y() - vertices[0].y())
        
        # 确定长边和旋转角度
        if bottom_vec.length() >= left_vec.length():
            # 底边是长边
            angle = math.atan2(bottom_vec.y(), bottom_vec.x())
        else:
            # 左边是长边，需要旋转90度
            angle = math.atan2(left_vec.y(), left_vec.x()) + math.pi/2
        
        # 转换为角度（QGIS使用度）
        self.rotation_angle = math.degrees(angle)
        
        return self.rotation_angle
    
    def focus_and_rotate(self):
        """聚焦到选定图层并旋转视图使长边水平"""
        angle = self.calculate_rotation_angle()
        if angle is None:
            QMessageBox.warning(self, lang["err"], lang['errRot'])
            return
        
        # 获取当前活动地图画布
        canvas = iface.mapCanvas()
        
        # 获取图层范围
        layer = self.layer_combo.currentData()
        extent = layer.extent()
        
        # 设置旋转角度
        canvas.setRotation(angle)
        
        # 缩放至图层范围
        canvas.setExtent(extent)
        canvas.refresh()
    
    def divide_rectangle(self, rect_geom, rows, cols, x_buffer, y_buffer):
        """将矩形分割为指定行数和列数的子矩形
    
        注意：rows始终沿长边(x方向)，cols沿短边(y方向)
        这是由get_min_area_rectangle()保证的
        """
        
        rect_vertices = rect_geom.asPolygon()[0][:-1]
        
        # 计算边向量
        bottom_vec = QgsVector(rect_vertices[1].x() - rect_vertices[0].x(),
                            rect_vertices[1].y() - rect_vertices[0].y())
        left_vec = QgsVector(rect_vertices[3].x() - rect_vertices[0].x(),
                            rect_vertices[3].y() - rect_vertices[0].y())
        
        # 计算实际长度（米）
        total_width = bottom_vec.length()
        total_height = left_vec.length()

        # 计算子地块尺寸
        cell_width = (total_width - (cols-1)*x_buffer) / cols
        cell_height = (total_height - (rows-1)*y_buffer) / rows

        # 验证有效尺寸
        if cell_width <=0 or cell_height <=0:
            raise ValueError(lang["errNegative"])
        
        # 标准化向量
        width_step = bottom_vec.normalized() * (cell_width + x_buffer)
        height_step = left_vec.normalized() * (cell_height + y_buffer)
        subplots = []
        for row in range(rows):
            for col in range(cols):
                # 计算起始点
                origin = QgsPointXY(
                    rect_vertices[0].x() + width_step.x()*col + height_step.x()*row,
                    rect_vertices[0].y() + width_step.y()*col + height_step.y()*row
                )
                
                # 构建子地块
                points = [
                    origin,
                    QgsPointXY(origin.x() + cell_width*bottom_vec.normalized().x(),
                            origin.y() + cell_width*bottom_vec.normalized().y()),
                    QgsPointXY(origin.x() + cell_width*bottom_vec.normalized().x() + cell_height*left_vec.normalized().x(),
                            origin.y() + cell_width*bottom_vec.normalized().y() + cell_height*left_vec.normalized().y()),
                    QgsPointXY(origin.x() + cell_height*left_vec.normalized().x(),
                            origin.y() + cell_height*left_vec.normalized().y()),
                    origin  # 闭合多边形
                ]
                subplots.append(QgsGeometry.fromPolygonXY([points]))
        
        return subplots
    
    def preview(self):
        """预览分割结果"""
        if not self.validate_input():
            return
        
        # 获取参数
        layer = self.layer_combo.currentData()
        feature = next(layer.getFeatures())
        geom = feature.geometry()
        
        # 获取最小面积外接矩形
        rect_geom = self.get_min_area_rectangle(geom)
        if not rect_geom:
            QMessageBox.warning(self, lang["err"], lang['errMinRect'])
            return
        
        rows = int(self.rows_edit.text())
        cols = int(self.cols_edit.text())
        x_buffer = float(self.x_buffer_edit.text())
        y_buffer = float(self.y_buffer_edit.text())
        
        # 分割矩形
        subplots = self.divide_rectangle(rect_geom, rows, cols, x_buffer, y_buffer)
        
        # 创建预览画布（如果不存在）
        if not self.preview_canvas:
            self.preview_canvas = QgsMapCanvas()
            self.preview_canvas.setWindowTitle(lang["prevWinTitle"])
            self.preview_canvas.setCanvasColor(Qt.white)
            # 设置为独立窗口，可关闭
            self.preview_canvas.setWindowFlags(Qt.Window)
        
        # 创建临时图层用于显示
        temp_layer = QgsVectorLayer("Polygon?crs=" + layer.crs().authid(), "preview", "memory")
        provider = temp_layer.dataProvider()
        
        # 添加字段
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        provider.addAttributes(fields)
        temp_layer.updateFields()
        
        # 添加要素
        features = []
        for i, subplot in enumerate(subplots):
            feat = QgsFeature(temp_layer.fields())
            feat.setGeometry(subplot)
            feat.setAttributes([i])
            features.append(feat)
        
        provider.addFeatures(features)  # 批量添加要素
        temp_layer.updateExtents()
        
        # 设置样式（新增这部分）
        subplot_symbol = QgsFillSymbol.createSimple({
            'color': '0,255,0,100',  # 半透明绿色
            'outline_color': 'black',
            'outline_width': '0.5'
        })
        temp_layer.renderer().setSymbol(subplot_symbol)
        
        # 确保范围有效
        if not temp_layer.extent().isNull():
            # 设置画布内容
            self.preview_canvas.setLayers([temp_layer, layer])
            extent = temp_layer.extent()
            if not layer.extent().isNull():
                extent.combineExtentWith(layer.extent())
            self.preview_canvas.setExtent(extent)
            # self.preview_canvas.refresh()
            self.preview_canvas.freeze(False)
            self.preview_canvas.refreshAllLayers()
            self.preview_canvas.showNormal()
        else:
            QMessageBox.warning(self, lang["err"], lang['errPrevRange'])

    
    def run(self):
        """执行分割操作"""
        if not self.validate_input():
            return
        
        # 获取参数
        layer = self.layer_combo.currentData()
        feature = next(layer.getFeatures())
        geom = feature.geometry()
        
        # 获取最小面积外接矩形
        rect_geom = self.get_min_area_rectangle(geom)
        if not rect_geom:
            QMessageBox.warning(self, lang["err"], lang['errMinRect'])
            return
        
        rows = int(self.rows_edit.text())
        cols = int(self.cols_edit.text())
        x_buffer = float(self.x_buffer_edit.text())
        y_buffer = float(self.y_buffer_edit.text())
        
        # 分割矩形
        subplots = self.divide_rectangle(rect_geom, rows, cols, x_buffer, y_buffer)
        
        # 确定输出CRS
        dom_layer = self.dom_combo.currentData()
        target_crs = dom_layer.crs() if dom_layer else layer.crs()
        if target_crs.isGeographic():
            QMessageBox.warning(self, lang["err"], lang["errMeterCRS"])
            return

        # subplots（rect_geom） 坐标转换到目标CRS
        original_crs = layer.crs()
        transform = QgsCoordinateTransform(original_crs, target_crs, QgsProject.instance())
        rect_geom.transform(transform)
        
        # 创建输出图层
        if self.output_edit.text():
            output_path = self.output_edit.text()
            output_layer = QgsVectorLayer("Polygon?crs=" + target_crs.authid(), "subplots", "memory")
        else:
            # 创建临时文件
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, "subplots_temp.shp")
            output_layer = QgsVectorLayer("Polygon?crs=" + target_crs.authid(), "subplots_temp", "memory")
        
        provider = output_layer.dataProvider()
        
        # 添加字段
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        fields.append(QgsField("row", QVariant.Int))
        fields.append(QgsField("col", QVariant.Int))
        provider.addAttributes(fields)
        output_layer.updateFields()
        
        # 添加要素
        for i, subplot in enumerate(subplots):
            feat = QgsFeature()
            feat.setGeometry(subplot)
            row = i // cols
            col = i % cols
            feat.setAttributes([i, row+1, col+1])  # 从1开始计数
            provider.addFeature(feat)
        
        output_layer.updateExtents()
        
        # 保存到文件
        if self.output_edit.text():
            error = QgsVectorFileWriter.writeAsVectorFormat(
                output_layer, 
                output_path, 
                "UTF-8", 
                output_layer.crs(), 
                "ESRI Shapefile"
            )
            
            if error[0] != QgsVectorFileWriter.NoError:
                QMessageBox.warning(self, lang["err"], f"{lang['errSave']}: {error[1]}")
                return
            
            # 重新加载保存的文件
            saved_layer = QgsVectorLayer(output_path, os.path.basename(output_path)[:-4], "ogr")
            if saved_layer.isValid():
                QgsProject.instance().addMapLayer(saved_layer)
                QMessageBox.information(self, lang['success'], f"{lang['sucSave']}: {output_path}")
            else:
                QMessageBox.warning(self, lang["err"], lang['errSaveLoad'])
        else:
            # 添加临时图层到项目
            QgsProject.instance().addMapLayer(output_layer)
            QMessageBox.information(self, lang['success'], lang['sucSaveTemp'])
        
        self.accept()

dialog = SubplotDivisionDialog()
dialog.exec_()
