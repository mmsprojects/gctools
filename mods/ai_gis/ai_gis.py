# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AIGIS
                                 A QGIS plugin
 Modelos de inteligência artificial no Qgis
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-10-06
        git sha              : $Format:%H$
        copyright            : (C) 2021 by MMS
        email                : mateusmelosiqueira@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
import sys 
sys.path.append(os.path.join(os.path.dirname(__file__),'lib'))
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon, QColor, QPixmap
from qgis.PyQt.QtWidgets import QWidget, QAction, QFileDialog, QTableWidget, QTableWidgetItem, QGridLayout
#from PyQt5.QtCore import QVariant
# Initialize Qt resources from file resources.py
#from .resources import *
# Import the code for the dialog
from .ai_gis_dialog import AIGISDialog

from qgis.core import QgsVectorFileWriter

import os.path
from yolov5 import YOLOv5

#from sahi.model import Yolov5DetectionModel
from sahi import AutoDetectionModel
from sahi.utils.cv import read_image, visualize_object_predictions
from sahi.utils.file import download_from_url
from sahi.predict import get_prediction, get_sliced_prediction, predict

from PIL import Image
Image.MAX_IMAGE_PIXELS = 10000000000
#import yolov5
from osgeo import gdal
# import gdal
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from osgeo import osr
from PyQt5.QtCore import QThread, pyqtSignal
import sqlite3
# import osr
import multiprocessing

class WorkerInference(QThread):
    def __init__(self, plugin_dir, weight, file_folder_status, img_dir, images, img_size, is_slice, confidence, overlap, is_pontos, is_poligonos):
        QThread.__init__(self)
        self.stp = False
        self.plugin_dir = plugin_dir
        self.file_folder_status = file_folder_status
        self.img_dir = img_dir
        self.images = images
        self.img_size = img_size
        self.is_slice = is_slice
        self.confidence = confidence
        self.overlap = overlap
        self.weight = weight
        self.is_pontos = is_pontos
        self.is_poligonos = is_poligonos


    up_list = pyqtSignal(list)
    results = pyqtSignal(list)
    def run(self):
        self.inference()

    def inference(self):
        print("ok")
        if not self.stp:
            # set model params
            # model_path = "yolov5/weights/yolov5s.pt" # it automatically downloads yolov5s model to given path


            self.device = "cpu"  # or "cpu"
            #self.weight = None

            if self.is_slice:
                # detection_model = Yolov5DetectionModel(
                # model_path=self.weight,
                # prediction_score_threshold=float(self.dlg.cb_confidence.currentText()),
                # device="cpu",  # or 'cuda'
                # )
                detection_model = AutoDetectionModel.from_pretrained(
                    model_type='yolov5',
                    model_path=self.weight,
                    confidence_threshold=float(self.confidence),
                    device="cpu",  # or 'cuda:0'
                )

                if (self.file_folder_status == 1):
                    image = read_image(self.img_dir)

                    result = get_sliced_prediction(
                        image,
                        detection_model,
                        slice_height=self.img_size,
                        slice_width=self.img_size,
                        overlap_height_ratio=float(self.overlap),
                        overlap_width_ratio=float(self.overlap)
                    )
                    if (self.dlg.cb_mostrar_imagem.isChecked()):
                        visualization_result = visualize_object_predictions(
                            image,
                            object_prediction_list=result.object_prediction_list,
                            output_dir=os.path.join(self.plugin_dir, 'temp'),
                            file_name="temp_prediction",
                        )
                        # Image(os.path.join(self.plugin_dir,'temp','temp_prediction.png'))
                        img = Image.open(os.path.join(self.plugin_dir, 'temp', 'temp_prediction.png'))

                        img.show()
                    i = 0
                    if (self.dlg.cb_poligonos.isChecked()):
                        object_prediction_list = result.object_prediction_list
                        raster = gdal.Open(self.img_dir,gdal.GA_ReadOnly)
                        proj = osr.SpatialReference(wkt=raster.GetProjection())
                        epsg = int(proj.GetAttrValue('AUTHORITY', 1))
                        self.polygon = QgsVectorLayer('Polygon?crs=epsg:{}&index=yes'.format(epsg), 'poligonos_a',
                                                      "memory")
                        self.point = QgsVectorLayer('Point?crs=epsg:{}&index=yes'.format(epsg), 'pontos_p',
                                                    "memory")
                        pr = self.polygon.dataProvider()
                        pr.addAttributes([QgsField("id", QVariant.Int), QgsField("classe", QVariant.String),
                                          QgsField("classe_id", QVariant.Int), QgsField("score", QVariant.Double)])
                        pr_p = self.point.dataProvider()
                        pr_p.addAttributes([QgsField("id", QVariant.Int), QgsField("classe", QVariant.String),
                                            QgsField("classe_id", QVariant.Int),
                                            QgsField("score", QVariant.Double)])

                        fields = self.polygon.fields()

                        self.polygon.updateFields()
                        self.polygon.commitChanges()
                        self.polygon.startEditing()
                        self.point.updateFields()
                        self.point.commitChanges()
                        self.point.startEditing()
                        for pred in object_prediction_list:
                            feat = QgsFeature()
                            feat.setFields(fields)
                            feat_p = QgsFeature()
                            feat_p.setFields(fields)
                            pred_coco = pred.to_coco_prediction().json
                            box = pred_coco['bbox']
                            classe = pred_coco['category_name']
                            classe_id = pred_coco['category_id']
                            score = round(pred.score.value, 2)
                            feat.setAttributes([i, classe, classe_id, score])
                            feat_p.setAttributes([i, classe, classe_id, score])
                            xmin = box[0]
                            ymin = box[1]
                            xmax = xmin + box[2]
                            ymax = ymin + box[3]
                            x1, y1 = self.pixel2coord(self.img_dir, xmin, ymin)
                            x2, y2 = self.pixel2coord(self.img_dir, xmax, ymin)
                            x3, y3 = self.pixel2coord(self.img_dir, xmax, ymax)
                            x4, y4 = self.pixel2coord(self.img_dir, xmin, ymax)
                            # print(self.pixel2coord(self.img_dir,0,0))
                            geom = QgsGeometry.fromPolygonXY(
                                [[QgsPointXY(x1, y1), QgsPointXY(x2, y2), QgsPointXY(x3, y3), QgsPointXY(x4, y4)]])
                            geom_p = geom.centroid()
                            feat.setGeometry(geom)
                            feat_p.setGeometry(geom_p)
                            pr.addFeatures([feat])
                            pr_p.addFeatures([feat_p])
                            self.polygon.updateExtents()
                            self.point.updateExtents()
                            i = i + 1
                            # print(geom)
                        self.polygon.commitChanges()
                        self.point.commitChanges()
                        QgsProject.instance().addMapLayers([self.polygon])
                        if (self.dlg.cb_pontos.isChecked()):
                            QgsProject.instance().addMapLayers([self.point])
                #PROCESSAR DIRETÓRIO
                elif (self.file_folder_status == 0):
                    #images = [os.path.basename(x) for x in os.listdir(self.img_dir)]

                    process = []
                    total = len(self.images)
                    for i,img in enumerate(self.images):
                        print(os.path.join(self.img_dir, img))

                        image = read_image(os.path.join(self.img_dir, img))
                        print("pre slice")
                        result = get_sliced_prediction(
                            image,
                            detection_model,
                            slice_height=self.img_size,
                            slice_width=self.img_size,
                            overlap_height_ratio=float(self.overlap),
                            overlap_width_ratio=float(self.overlap)
                        )

                        #object_prediction_list = result["object_prediction_list"]
                        object_prediction_list = result.object_prediction_list


                        for pred in object_prediction_list:

                            pred_coco = pred.to_coco_prediction().json
                            box = pred_coco['bbox']
                            classe = pred_coco['category_name']
                            classe_id = pred_coco['category_id']
                            score = round(pred.score.value, 2)

                            xmin = box[0]
                            ymin = box[1]
                            xmax = xmin + box[2]
                            ymax = ymin + box[3]
                            x1, y1 = self.pixel2coord(os.path.join(self.img_dir, img), xmin, ymin)
                            x2, y2 = self.pixel2coord(os.path.join(self.img_dir, img), xmax, ymin)
                            x3, y3 = self.pixel2coord(os.path.join(self.img_dir, img), xmax, ymax)
                            x4, y4 = self.pixel2coord(os.path.join(self.img_dir, img), xmin, ymax)
                            # print(self.pixel2coord(self.img_dir,0,0))

                            res = {'x1': x1,
                                   'y1': y1,
                                   'x2': x2,
                                   'y2': y2,
                                   'x3': x3,
                                   'y3': y3,
                                   'x4': x4,
                                   'y4': y4,
                                   'id':i,
                                   'classe':classe,
                                   'classe_id':classe_id,
                                   'score': score}

                            self.results.emit([res])


                            # print(geom)
                        print(i)
                        print([int(100*i/total)])
                        self.up_list.emit([int(100*i/total)])


            else:
                self.yolov5 = YOLOv5(self.weight, self.device)

                if (self.file_folder_status == 0):
                    images = [os.path.basename(x) for x in os.listdir(self.img_dir)]
                    for img in images:
                        if (self.dlg.cb_size == '1280'):
                            results = self.yolov5.predict(os.path.join(self.img_dir, img), size=1280)
                            self.img_size = 1280
                        elif (self.dlg.cb_size == '640'):
                            results = self.yolov5.predict(os.path.join(self.img_dir, img), size=640)
                            self.img_size = 1280
                        else:
                            results = self.yolov5.predict(os.path.join(self.img_dir, img), size=640)
                            self.img_size = 640
                        if (self.dlg.cb_mostrar_imagem.isChecked()):
                            results.show()
                elif (self.file_folder_status == 1):
                    if (self.dlg.cb_size == '1280'):
                        results = self.yolov5.predict(self.img_dir, size=1280)
                        self.img_size = 1280
                    elif (self.dlg.cb_size == '640'):
                        results = self.yolov5.predict(self.img_dir, size=640)
                        self.img_size = 1280
                    else:
                        results = self.yolov5.predict(self.img_dir, size=640)
                        self.img_size = 640
                    if (self.dlg.cb_mostrar_imagem.isChecked()):
                        results.show()

            # perform inference with larger input size
            # results = yolov5.predict(image1, size=1280)

            # perform inference with test time augmentation
            # results = yolov5.predict(image1, augment=True)

            # perform inference on multiple images
            # results = yolov5.predict([image1, image2], size=1280, augment=True)

            # show detection bounding boxes on image
            # results.show()

            # save results into "results/" folder
            # results.save(save_dir='results/')

    def pixel2coord(self, raster_path, x, y):
        raster = gdal.Open(raster_path,gdal.GA_ReadOnly)
        xoff, a, b, yoff, d, e = raster.GetGeoTransform()
        xp = a * x + b * y + a * 0.5 + b * 0.5 + xoff
        yp = d * x + e * y + d * 0.5 + e * 0.5 + yoff
        return xp, yp

    # def boxes2QgsPolygons(self,boxes):

    # def boxes2QgsPoints(self,boxes):

class AIGIS:
    def __init__(self, iface, cls_main):

        # Save reference to the QGIS interface
        self.gctools = cls_main
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = self.gctools.plugin_dir

        
    def updateBar(self,data):
        print(data)
        self.dlg.gcbar_geral.value = int(data[0])
    def setworker(self):

        self.create_results_layers()
        #get images
        images = []
        for row in range(0, self.dlg.table.rowCount()):
            images.append(self.dlg.table.item(row, 2).text())
            img_dir = self.dlg.table.item(row, 1).text()

        #get model_path
        self.model_path = os.path.join(self.plugin_dir, 'mods', 'ai_gis', 'weights')
        print(self.model_path)

        #get weight
        weight = self.getmodel()

        #get img_size
        img_size = self.getsize()

        #is sliced
        if self.dlg.cb_slice_imagem.isChecked():
            is_slice = 1
        else:
            is_slice = 0

        #get pontos
        if self.dlg.cb_pontos.isChecked():
            is_pontos = 1
        else:
            is_pontos = 0

        #get poligonos
        if self.dlg.cb_poligonos.isChecked():
            is_poligonos = 1
        else:
            is_poligonos = 0

        #get confidence
        confidence = float(self.dlg.cb_confidence.currentText())

        #get overlap
        overlap = float(self.dlg.cb_overlap.currentText())

        #set Worker Thread
        self.worker_inferencer = WorkerInference(self.plugin_dir,
                                                 weight,
                                                 self.file_folder_status,
                                                 self.img_dir,
                                                 images,
                                                 img_size,
                                                 is_slice,
                                                 confidence,
                                                 overlap,
                                                 is_pontos,
                                                 is_poligonos)

        self.worker_inferencer.up_list.connect(self.updateBar)
        self.worker_inferencer.results.connect(self.addfeature2layer)
        self.worker_inferencer.run()


    def getsize(self):
        if (self.dlg.cb_size == '1280'):
            # results = self.yolov5.predict(self.img_dir, size=1280)
            self.img_size = 1280
        elif (self.dlg.cb_size == '640'):
            # results = self.yolov5.predict(self.img_dir, size=640)
            self.img_size = 1280
        else:
            # results = self.yolov5.predict(self.img_dir, size=640)
            self.img_size = 640

        return self.img_size

    def getmodel(self):
        # init yolov5 model
        if (self.dlg.cb_tipo.currentText() == 'Classes Gerais (COCO Dataset)'):
            self.weight = os.path.join(self.model_path, 'yolov5x6.pt')
        elif (self.dlg.cb_tipo.currentText() == 'Arvores_10cm'):
            self.weight = os.path.join(self.model_path, 'arvores_mms_v1.pt')
        elif (self.dlg.cb_tipo.currentText() == 'Arvores_1m'):
            self.weight = os.path.join(self.model_path, 'arvores_mms_v2.pt')
        elif (self.dlg.cb_tipo.currentText() == 'Lixao_24cm'):
            self.weight = os.path.join(self.model_path, 'lixao_v1.pt')
        else:
            self.weight = None

        return self.weight

    def dir_file(self):
        self.file_folder_status = 1
        self.img_dir = QFileDialog.getOpenFileName()[0]
        self.dlg.line_file.setText(self.img_dir)
        print(self.img_dir)

    def dir_folder(self):
        self.file_folder_status = 0
        #self.img_dir = QFileDialog.getExistingDirectory()

        filenames, _ = QFileDialog.getOpenFileNames(
                                                    None,
                                                    "QFileDialog.getOpenFileNames()",
                                                    "",
                                                    "Tiff (*.tif);;All Files (*);",)
        if filenames:
            self.img_dir = os.path.dirname(filenames[0])
            self.dlg.line_file.setText(self.img_dir)
            #fill table
            images = [os.path.basename(x) for x in filenames]

            self.dlg.show()
            for x,im in enumerate(images):
                row = self.dlg.table.rowCount()

                color_pend = QColor()
                color_pend.setRgb(89, 141, 214)
                icon_pend = QIcon()
                icon_pend.addPixmap(QPixmap(os.path.join(self.plugin_dir, "icons", "pend.png")), QIcon.Normal, QIcon.Off)

                item_id = QTableWidgetItem()
                item_id.setCheckState(2)
                item_id.setText(str(x))

                item_img_dir = QTableWidgetItem()
                item_img_dir.setText(str(self.img_dir))

                item_img = QTableWidgetItem()
                item_img.setText(str(im))

                item_proc = QTableWidgetItem()
                item_proc.setText(str("PEND"))
                item_proc.setBackground(color_pend)
                item_proc.setIcon(icon_pend)


                self.dlg.table.insertRow(row)
                self.dlg.table.setItem(row, 0, item_id) #id
                self.dlg.table.setItem(row, 1, item_img_dir) #pasta
                self.dlg.table.setItem(row, 2, item_img) #imagem
                self.dlg.table.setItem(row, 3, item_proc) #status

            raster = gdal.Open(os.path.join(self.img_dir, images[0]),gdal.GA_ReadOnly)
            proj = osr.SpatialReference(wkt=raster.GetProjection())
            self.epsg = int(proj.GetAttrValue('AUTHORITY', 1))
            self.dlg.ln_srid.setText(str(self.epsg))


    def create_results_layers(self):
        self.srid = int(self.dlg.ln_srid.displayText())

        if self.dlg.cb_memory.isChecked():
            self.polygon = QgsVectorLayer('Polygon?crs=epsg:{}&index=yes'.format(self.epsg), 'poligonos_a',
                                          "memory")
            self.point = QgsVectorLayer('Point?crs=epsg:{}&index=yes'.format(self.epsg), 'pontos_p',
                                        "memory")
            self.pr = self.polygon.dataProvider()
            self.pr.addAttributes([QgsField("id", QVariant.Int), QgsField("classe", QVariant.String),
                                   QgsField("classe_id", QVariant.Int),
                                   QgsField("score", QVariant.Double)])
            self.pr_p = self.point.dataProvider()
            self.pr_p.addAttributes([QgsField("id", QVariant.Int), QgsField("classe", QVariant.String),
                                     QgsField("classe_id", QVariant.Int),
                                     QgsField("score", QVariant.Double)])

            QgsProject.instance().addMapLayers([self.point])
            if (self.dlg.cb_poligonos.isChecked()):
                QgsProject.instance().addMapLayers([self.polygon])
        else:
            output = self.dlg.ln_output.displayText()
            dir = os.path.dirname(output)
            name = os.path.basename(output).replace(".shp","")
            out_a = os.path.join(dir,name+"_a.shp")
            out_p = os.path.join(dir,name+"_p.shp")
            polygon = QgsVectorLayer('Polygon?crs=epsg:{}&index=yes'.format(self.epsg), name+"_a",
                                          "memory")
            point = QgsVectorLayer('Point?crs=epsg:{}&index=yes'.format(self.epsg), name+"_p",
                                        "memory")


            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = 'ESRI Shapefile'
            context = QgsProject.instance().transformContext()
            # since QGIS 3.20 you should use writeAsVectorFormatV3
            QgsVectorFileWriter.writeAsVectorFormatV3(polygon, out_a, context, options)
            QgsVectorFileWriter.writeAsVectorFormatV3(point, out_p, context, options)

            self.polygon = QgsVectorLayer(out_a, name+"_p.shp", "ogr")
            self.point = QgsVectorLayer(out_p, name+"_a.shp", "ogr")

            self.pr = self.polygon.dataProvider()
            self.pr.addAttributes([QgsField("id", QVariant.Int), QgsField("classe", QVariant.String),
                                   QgsField("classe_id", QVariant.Int),
                                   QgsField("score", QVariant.Double)])

            self.pr_p = self.point.dataProvider()
            self.pr_p.addAttributes([QgsField("id", QVariant.Int), QgsField("classe", QVariant.String),
                                     QgsField("classe_id", QVariant.Int),
                                     QgsField("score", QVariant.Double)])
            QgsProject.instance().addMapLayers([self.point])
            #if (self.dlg.cb_poligonos.isChecked()):
            QgsProject.instance().addMapLayers([self.polygon])

    def addfeature2layer(self, data):
        fields = self.polygon.fields()

        feat = QgsFeature()
        feat.setFields(fields)
        feat_p = QgsFeature()
        feat_p.setFields(fields)

        x1 = data[0]['x1']
        y1 = data[0]['y1']
        x2 = data[0]['x2']
        y2 = data[0]['y2']
        x3 = data[0]['x3']
        y3 = data[0]['y3']
        x4 = data[0]['x4']
        y4 = data[0]['y4']

        i = data[0]['id']
        classe = data[0]['classe']
        classe_id = data[0]['classe_id']
        score = data[0]['score']


        geom = QgsGeometry.fromPolygonXY(
            [[QgsPointXY(x1, y1), QgsPointXY(x2, y2), QgsPointXY(x3, y3),
              QgsPointXY(x4, y4)]])

        feat.setAttributes([i, classe, classe_id, score])
        feat_p.setAttributes([i, classe, classe_id, score])

        geom_p = geom.centroid()
        feat.setGeometry(geom)
        feat_p.setGeometry(geom_p)
        self.pr.addFeatures([feat])
        self.pr_p.addFeatures([feat_p])
        self.polygon.updateExtents()
        self.point.updateExtents()

        self.polygon.updateFields()
        self.polygon.commitChanges()
        self.polygon.startEditing()
        self.point.updateFields()
        self.point.commitChanges()
        self.point.startEditing()

    def saveproject(self):
        qwidget = QWidget()
        savedirname, _ = QFileDialog.getSaveFileName(
            qwidget, "Save project", "", " SQLite (*.sqlite)")
        if savedirname:
            conn = sqlite3.connect(savedirname)
            c = conn.cursor()
            c.execute('PRAGMA journal_mode=wal')

    def openproject(self):
        qfd = QFileDialog()
        filter = "SQLite (*.sqlite)"
        openeddirname = QFileDialog.getOpenFileName(qfd, "Open project", "", filter)[0]

        if openeddirname:
            conn = sqlite3.connect(openeddirname)
            c = conn.cursor()
            c.execute('PRAGMA journal_mode=wal')

    def setmemoryoutput(self):
        if self.dlg.cb_memory.isChecked():
            self.dlg.ln_output.setText("[Memory Output]")
            self.dlg.pb_salvar.setEnabled(False)
        else:
            self.dlg.pb_salvar.setEnabled(True)
            if len(self.dlg.line_file.displayText())>0:
                if self.dlg.ln_output.displayText()=='[Memory Output]':
                    self.dlg.ln_output.setText("")
                else:
                    return
            else:
                self.dlg.ln_output.setText("")

    def setoutput(self):
        qwidget = QWidget()
        savedirname, _ = QFileDialog.getSaveFileName(
            qwidget, "Save Poligon/Points Shape", "", " Shapefile (*.shp)")
        if savedirname:
            print("caminho de saida obtido")
            self.dlg.ln_output.setText(savedirname)
    def run(self):
        self.dlg = AIGISDialog()
        self.dlg.pb_inference.clicked.connect(self.setworker)
        self.dlg.pb_dir_file.clicked.connect(self.dir_file)
        self.dlg.pb_dir_folder.clicked.connect(self.dir_folder)
        self.dlg.cb_confidence.setCurrentText('0.80')
        self.file_folder_status = None
        # show the dialog
        self.dlg.show()
        self.dlg.actionSalvar.triggered.connect(self.saveproject)
        self.dlg.actionAbrir.triggered.connect(self.openproject)
        self.dlg.cb_memory.toggled.connect(self.setmemoryoutput)
        self.dlg.pb_salvar.clicked.connect(self.setoutput)