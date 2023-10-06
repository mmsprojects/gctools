
"""***************************************************************************
 *   @titulo: Ação Caracterização
 *   @autor: Mateus Melo Siqueira/ Consultoria Topocart
 *   @email: mateus.melo@topocart.com.br
 *   @data: 2022-05-09
 *   @versao: 1.00
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************"""

#Importação das bibliotecas
from qgis.core import QgsWkbTypes, QgsGeometry, QgsPoint, QgsProject, QgsMapLayerProxyModel
from qgis.gui import QgsRubberBand, QgsMapLayerComboBox, QgsFieldComboBox
from PyQt5.QtWidgets import QTabWidget, QFrame,QAbstractItemView,  QMessageBox, QShortcut, QDockWidget, QComboBox, QLineEdit, QTableWidget, QTableWidgetItem, QCheckBox, QGridLayout, QLabel, QWidget, QSizePolicy,QSpacerItem, QPushButton
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtGui import QColor, QCursor, QPixmap, QIcon, QImage
import base64
import io
from PIL import Image, ImageQt
from functools import partial
import psycopg2
import psycopg2.extras
import webbrowser
import os
#Classe principal - interface do Qgis
self = qgis.utils.iface


#Classe principal - dialogo de verificacao
class Verificacao(QDockWidget):
    def __init__(self,cls_qgis=None,parent=None):
        super(Verificacao, self).__init__()
        self.cls_qgis = cls_qgis
        self.canvas = self.cls_qgis.mapCanvas()
        
        
        self.dic_field_alias = {
            "field_verificacao": ["revisao"] }
        
        self.dic_campos_lt = {'ocupacao':{1:'Não Edificado',
                                          2:'Ruínas',
                                          3:'Construção Paralisada',
                                          4:'Construção em Andamento',
                                          5:'Construído'
                                          },
                              'situacao_lote':{1:'Meio de Quadra',
                                               2:'Esquina 2 Frentes',
                                               3:'Esquina + de 2 Frentes',
                                               4:'Vila',
                                               5:'Condominio Horizontal',
                                               6:'Encravado',
                                               7:'Gleba',
                                               8:'Aglomerado'  
                                           },
                               'classe':{1:'AB Com Muro',
                                         2:'AB Sem Muro',
                                         3:'CD Com Muro',
                                         4:'CD Sem Muro'},
                               'calcada':{1:'Sim',
                                          2:'Não'
                                            },
                               'utilizacao':{1:'Sem Uso',
                                             2:'Residencial',
                                             3:'Comercial',
                                             4:'Serviços',
                                             5:'Serviços Públicos',
                                             6:'Industrial',
                                             7:'Religiosa',
                                             8:'Mista'
                                             }
                                }
        self.dic_campos_un = {'situacao_unidade':{1:'Frente',
                                                  2:'Fundos',
                                                  3:'Sup Frente',
                                                  4:'Sup Fundos',
                                                  5:'Sobre Loja',
                                                  6:'Sub-Solo',
                                                  7:'Galeria'
                                                  },
                              'alinhamento':{1:'Alinhada',
                                             2:'Recuada',
                                             3:'Avançada'
                                            },
                              'estrutura':{1:'Alvenaria',
                                           2:'Madeira',
                                           3:'Metálica',
                                           4:'Concreto'
                                          },
                              'paredes':{1:'Sem',
                                         2:'Taipa',
                                         3:'Alvenaria',
                                         4:'Madeira Simples',
                                         5:'Concreto',
                                         6:'Adobe',
                                         7:'Madeira Nobre',
                                         8:'Tijolo Cerâmica'
                                        },
                               'revestimento_externo':{1:'Sem',
                                                       2:'Emboco',
                                                       3:'Reboco',
                                                       4:'Material Cerâmico',
                                                       5:'Madeira',
                                                       6:'Pintura',
                                                       7:'Especial',
                                                       8:'Mármore'
                                                       },
                               'cobertura':{1:'Palha',
                                            2:'Cimento Amianto',
                                            3:'Telha Barro',
                                            4:'Laje',
                                            5:'Metálico/Zinco'
                                            },
                               
                               'tipo_edificacao':{1:'Casas Residênciais',
                                                  2:'Construções Precárias',
                                                  3:'Apartamentos Res. em Edificações até 3 Pavimentos',
                                                  4:'Salas Comerciais',
                                                  5:'SLojas Edif. Para Comércio Serviços',
                                                  6:'Galpões Para Depósitos Fechados',
                                                  7:'Telheiros',
                                                  8:'Apartamentos Resid em Edificações até 4 Pavimentos',
                                                  9:'Shopping Centers',
                                                  10:'Edificações p/ Indústrias Exceto Galpões',
                                                  11:'Galpão Indústrial',
                                                  12:'Galpão para Comércio,Serv e Armazéns Abertos',
                                                  13:'Posto Gasolina',
                                                  14:'Apartamentos Resid em Edificações 5 Pav ou mais',
                                                  15:'Condomínios Residências Fechadas'
                                                 },
                               'conservacao':{1:'Ótima',
                                              2:'Boa',
                                              3:'Regular',
                                              4:'Ruim',
                                              5:'Péssima'
                                              },
                               'padrao_construtivo':{1:'Luxo',
                                                     2:'Alto',
                                                     3:'Médio',
                                                     4:'Baixo',
                                                     5:'Proletário',
                                                     6:'Rudimentar'
                                                     },
                               'outras_instalacoes':{1:'Piscina',
                                                     2:'Sauna',
                                                     3:'Quadra Esportiva',
                                                     4:'Sala Ginástica',
                                                     5:'Play Ground',
                                                     6:'Sem'
                                                     },
                                'posicionamento':{1:'Isolada',
                                                  2:'Conjugada',
                                                  3:'Geminada',
                                                  4:'Edifício'
                                                  }
                            }
        
        
        self.setObjectName('Dock Caracterização')
        self.setWindowTitle('Dock Caracterização')
        self.visibilityChanged.connect(self.close)
        #self.setTitleText('dock_rev')
        self.setAllowedAreas(Qt.RightDockWidgetArea)
        self.cls_qgis.addDockWidget(Qt.RightDockWidgetArea,self)
        
        self.layout = QGridLayout()
        r_=0
        self.map_unidades = QgsMapLayerComboBox()
        self.map_unidades.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.map_unidades.currentTextChanged.connect(self.changedMapUn)
        
        self.layout.addWidget(self.map_unidades,r_,1,1,2)
        r_+=1
        self.map_lote = QgsMapLayerComboBox()
        self.map_lote.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.map_lote.currentTextChanged.connect(self.changeMapLt)
        self.layout.addWidget(self.map_lote,r_,1,1,2)
        
        # r_+=1
        # self.field_verificacao = QgsFieldComboBox()
        # self.map_lote.currentTextChanged.connect(partial(self.fill_fcbs,self.map_lote,self.field_verificacao))
        # self.fill_fcbs(self.map_lote,self.field_verificacao)
        # self.layout.addWidget(self.field_verificacao,r_,1,1,2)
        
        
        r_+=1
        self.check_foto = QCheckBox(text='Abrir foto')
        self.check_foto.setChecked(True)
        self.layout.addWidget(self.check_foto,r_,1,1,2)
        
        r_+=1 
        self.line_password = QLineEdit()
        self.line_password.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.line_password,r_,1,1,2)
        
        r_+=1
        self.label_id_lote = QLabel(text='id_lote')
        self.layout.addWidget(self.label_id_lote,r_,1)
        #r_+=1
        self.label_id_un = QLabel(text='id_un')
        self.layout.addWidget(self.label_id_un,r_,2)
        r_+=1
        self.line_id_lote = QLineEdit()
        self.layout.addWidget(self.line_id_lote,r_,1)
        #r_+=1
        self.line_id_un = QLineEdit()
        self.layout.addWidget(self.line_id_un,r_,2)
        
        r_+=1
        self.sep_line1 = QFrame()
        self.sep_line1.setFrameShape(QFrame.HLine)
        self.layout.addWidget(self.sep_line1, r_,1,1,2)
        
        
        r_+=1
        
        self.pb_conect = QPushButton()
        icon_conect = "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"
        imgdata = base64.b64decode(icon_conect)
        image_pil = Image.open(io.BytesIO(imgdata))
        image_qt = ImageQt.ImageQt(image_pil)
        pixmap = QPixmap.fromImage(QImage(image_qt))
        icon_ = QIcon()
        icon_.addPixmap(pixmap)
        self.pb_conect.setIcon(icon_)
        self.pb_conect.setIconSize(QSize(15, 15))
        self.pb_conect.setFixedSize(QSize(20, 20))
        self.pb_conect.clicked.connect(self.criar_sinal)
        self.layout.addWidget(self.pb_conect,r_,1)
        
        self.pb_disconect = QPushButton()
        icon_conect = "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"
        imgdata = base64.b64decode(icon_conect)
        image_pil = Image.open(io.BytesIO(imgdata))
        image_qt = ImageQt.ImageQt(image_pil)
        pixmap = QPixmap.fromImage(QImage(image_qt))
        icon_ = QIcon()
        icon_.addPixmap(pixmap)
        self.pb_disconect.setIcon(icon_)
        self.pb_disconect.setIconSize(QSize(15, 15))
        self.pb_disconect.setFixedSize(QSize(20, 20))
        self.pb_disconect.clicked.connect(self.deletar_sinal)
        self.layout.addWidget(self.pb_disconect,r_,2)
        
        # self.pb_salvar = QPushButton()
        # icon_salvar = "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"
        # imgdata = base64.b64decode(icon_salvar)
        # image_pil = Image.open(io.BytesIO(imgdata))
        # image_qt = ImageQt.ImageQt(image_pil)
        # pixmap = QPixmap.fromImage(QImage(image_qt))
        # icon_ = QIcon()
        # icon_.addPixmap(pixmap)
        # self.pb_salvar.setIcon(icon_)
        # self.pb_salvar.setIconSize(QSize(15, 15))
        # self.pb_salvar.setFixedSize(QSize(20, 20))
        # self.pb_salvar.clicked.connect(self.salvar)
        # self.layout.addWidget(self.pb_salvar,r_,3)
        
        r_+=1
        lt_= 0
        self.tab = QTabWidget()
        self.tab_lt = QWidget()
        self.lt_layout = QGridLayout()
        
        
        self.pb_salvar_lt = QPushButton()
        icon_salvar = "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"
        imgdata = base64.b64decode(icon_salvar)
        image_pil = Image.open(io.BytesIO(imgdata))
        image_qt = ImageQt.ImageQt(image_pil)
        pixmap = QPixmap.fromImage(QImage(image_qt))
        icon_ = QIcon()
        icon_.addPixmap(pixmap)
        self.pb_salvar_lt.setIcon(icon_)
        self.pb_salvar_lt.setIconSize(QSize(15, 15))
        self.pb_salvar_lt.setFixedSize(QSize(20, 20))
        self.pb_salvar_lt.clicked.connect(self.setCamposLT)
        self.lt_layout.addWidget(self.pb_salvar_lt,r_,1,1,2)
        #Campos caracterizacao lote
        #Ocupacao
        lt_+=1
        self.label_lt_ocupacao = QLabel(text='ocupacao')
        self.lt_layout.addWidget(self.label_lt_ocupacao,lt_,1)
        self.cb_lt_ocupacao = QComboBox()
        self.lt_layout.addWidget(self.cb_lt_ocupacao,lt_,2)
        
        #Situacao Lote
        lt_+=1
        self.label_lt_situacao = QLabel(text='situacao_lote')
        self.lt_layout.addWidget(self.label_lt_situacao,lt_,1)
        self.cb_lt_situacao = QComboBox()
        self.lt_layout.addWidget(self.cb_lt_situacao,lt_,2)
        
        #classe
        lt_+=1
        self.label_lt_classe = QLabel(text='classe')
        self.lt_layout.addWidget(self.label_lt_classe,lt_,1)
        self.cb_lt_classe = QComboBox()
        self.lt_layout.addWidget(self.cb_lt_classe,lt_,2)
        
        #calcada
        lt_+=1
        self.label_lt_calcada = QLabel(text='calcada')
        self.lt_layout.addWidget(self.label_lt_calcada,lt_,1)
        self.cb_lt_calcada = QComboBox()
        self.lt_layout.addWidget(self.cb_lt_calcada,lt_,2)
        
        #utilizacao
        lt_+=1
        self.label_lt_utilizacao = QLabel(text='utilizacao')
        self.lt_layout.addWidget(self.label_lt_utilizacao,lt_,1)
        self.cb_lt_utilizacao = QComboBox()
        self.lt_layout.addWidget(self.cb_lt_utilizacao,lt_,2)
        
        self.tab_lt.setLayout(self.lt_layout)
        self.tab.addTab(self.tab_lt,'Lote')
        
        self.tab_un = QWidget()
        self.un_layout = QGridLayout()
        
        self.pb_salvar_un = QPushButton()
        icon_salvar = "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"
        imgdata = base64.b64decode(icon_salvar)
        image_pil = Image.open(io.BytesIO(imgdata))
        image_qt = ImageQt.ImageQt(image_pil)
        pixmap = QPixmap.fromImage(QImage(image_qt))
        icon_ = QIcon()
        icon_.addPixmap(pixmap)
        self.pb_salvar_un.setIcon(icon_)
        self.pb_salvar_un.setIconSize(QSize(15, 15))
        self.pb_salvar_un.setFixedSize(QSize(20, 20))
        self.pb_salvar_un.clicked.connect(self.setCamposUn)
        self.un_layout.addWidget(self.pb_salvar_un,0,4)
        
        #unidades do lote
        un_=0
        self.label_un_ids = QLabel(text='ID (unidade)')
        self.un_layout.addWidget(self.label_un_ids,un_,1)
        self.cb_un_ids = QComboBox()
        self.cb_un_ids.currentIndexChanged.connect(self.getCamposUn)
        self.un_layout.addWidget(self.cb_un_ids,un_,2)
        
        un_+=1
        self.sep_line2 = QFrame()
        self.sep_line2.setFrameShape(QFrame.HLine)
        self.un_layout.addWidget(self.sep_line2, un_,1,1,2)
        
        #Campos caracterizacao unidade
        #situacao_unidade
        un_+= 1
        self.label_un_situacao_unidade = QLabel(text='Situação')
        self.un_layout.addWidget(self.label_un_situacao_unidade,un_,1)
        self.cb_un_situacao_unidade = QComboBox()
        self.un_layout.addWidget(self.cb_un_situacao_unidade,un_,2)
        
        #alinhamento
        #un_+= 1
        self.label_un_alinhamento = QLabel(text='Alinhamento')
        self.un_layout.addWidget(self.label_un_alinhamento,un_,3)
        self.cb_un_alinhamento = QComboBox()
        self.un_layout.addWidget(self.cb_un_alinhamento,un_,4)
        
        #estrutura
        un_+= 1
        self.label_un_estrutura = QLabel(text='Estrutura')
        self.un_layout.addWidget(self.label_un_estrutura,un_,1)
        self.cb_un_estrutura = QComboBox()
        self.un_layout.addWidget(self.cb_un_estrutura,un_,2)
        
        #paredes
        #un_+= 1
        self.label_un_paredes = QLabel(text='Paredes')
        self.un_layout.addWidget(self.label_un_paredes,un_,3)
        self.cb_un_paredes = QComboBox()
        self.un_layout.addWidget(self.cb_un_paredes,un_,4)
        
        #revestimento
        un_+= 1
        self.label_un_revestimento = QLabel(text='Revestimento')
        self.un_layout.addWidget(self.label_un_revestimento,un_,1)
        self.cb_un_revestimento = QComboBox()
        self.un_layout.addWidget(self.cb_un_revestimento,un_,2)
        
        #cobertura
        #un_+= 1
        self.label_un_cobertura = QLabel(text='Cobertura')
        self.un_layout.addWidget(self.label_un_cobertura,un_,3)
        self.cb_un_cobertura = QComboBox()
        self.un_layout.addWidget(self.cb_un_cobertura,un_,4)
        
        #tipo_edificacao
        un_+= 1
        self.label_un_tipo_edif = QLabel(text='Tipo Edificação')
        self.un_layout.addWidget(self.label_un_tipo_edif,un_,1)
        self.cb_un_tipo_edif = QComboBox()
        self.un_layout.addWidget(self.cb_un_tipo_edif,un_,2)
        
        #padrao_construtivo
        #un_+= 1
        self.label_un_padrao_const = QLabel(text='Padrão Const.')
        self.un_layout.addWidget(self.label_un_padrao_const,un_,3)
        self.cb_un_padrao_const = QComboBox()
        self.un_layout.addWidget(self.cb_un_padrao_const,un_,4)
        
        #conservacao
        un_+= 1
        self.label_un_conservacao = QLabel(text='Conservação')
        self.un_layout.addWidget(self.label_un_conservacao,un_,1)
        self.cb_un_conservacao = QComboBox()
        self.un_layout.addWidget(self.cb_un_conservacao,un_,2)

        #outras_instalacoes
        #un_+=1
        self.label_un_outras_instalac = QLabel(text='Outras Instalações')
        self.un_layout.addWidget(self.label_un_outras_instalac,un_,3)
        self.cb_un_outras_instalac = QComboBox()
        self.un_layout.addWidget(self.cb_un_outras_instalac ,un_,4)
        
        un_+=1
        self.label_un_posicionamento = QLabel(text='Posicionamento')
        self.un_layout.addWidget(self.label_un_posicionamento,un_,1)
        self.cb_un_posicionamento = QComboBox()
        self.un_layout.addWidget(self.cb_un_posicionamento ,un_,2)
        
        
        self.tab_un.setLayout(self.un_layout)
        self.tab.addTab(self.tab_un,'Unidade')
        
        self.layout.addWidget(self.tab,r_,1,1,2)
        
        self.connected = False
        self.rb_center = None
        self.last_lote_id = None
        self.rb_center = QgsRubberBand(self.canvas, QgsWkbTypes.PointGeometry)
        self.rb_center.setWidth(15)
        self.rb_center.setColor(QColor(0, 0, 255))
        color_ = QColor(Qt.lightGray)
        color_.setAlpha(90)
        self.rb_center.setFillColor(color_)
        

        self.layer_un_spc_idx = None
        self.layer_lt_spc_idx = None
        
        #self.frame_rev = QFrame()
        #self.addWidget(self.layout)
        #Cria a conexão com o mapa
        self.spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(self.spacer)
       
        
        self.wd = QWidget()
        self.wd.setLayout(self.layout)
        self.setWidget(self.wd)
        
        if not self.cls_qgis.sinal_status:
            self.cls_qgis.sinal_status = self.criar_sinal()
        
        self.setupindex()
    
    
    def salvar(self):
        self.setCamposLT()
        pass
    
    def getCamposLT(self):
        #apaga os combobox lote
        self.cb_lt_ocupacao.clear()
        self.cb_lt_situacao.clear()
        self.cb_lt_classe.clear()
        self.cb_lt_calcada.clear()
        self.cb_lt_utilizacao.clear()
        
        #insere dominios campos lote

        self.cb_lt_ocupacao.insertItems(1,list(self.dic_campos_lt['ocupacao'].values())+[''])
        self.cb_lt_situacao.insertItems(1,list(self.dic_campos_lt['situacao_lote'].values())+[''])
        self.cb_lt_classe.insertItems(1,list(self.dic_campos_lt['classe'].values())+[''])
        self.cb_lt_calcada.insertItems(1,list(self.dic_campos_lt['calcada'].values())+[''])
        self.cb_lt_utilizacao.insertItems(1,list(self.dic_campos_lt['utilizacao'].values())+[''])
        
        lotes = self.map_lote.currentLayer()
        if self.line_id_lote.displayText()!='':
            id_lote = int(self.line_id_lote.displayText())
            feat_lt = lotes.getFeature(id_lote)
            if feat_lt['ocupacao']!=None:
                self.cb_lt_ocupacao.setCurrentText(self.dic_campos_lt['ocupacao'][feat_lt['ocupacao']])
            else:
                self.cb_lt_ocupacao.setCurrentText('')
            if feat_lt['situacao_lote']!=None:
                self.cb_lt_situacao.setCurrentText(self.dic_campos_lt['situacao_lote'][feat_lt['situacao_lote']])
            else:
                self.cb_lt_situacao.setCurrentText('')
            if feat_lt['classe']!=None:
                self.cb_lt_classe.setCurrentText(self.dic_campos_lt['classe'][feat_lt['classe']])
            else:
                self.cb_lt_classe.setCurrentText('')
            if feat_lt['calcada']!=None:
                self.cb_lt_calcada.setCurrentText(self.dic_campos_lt['calcada'][feat_lt['calcada']])
            else:
                self.cb_lt_calcada.setCurrentText('')
            if feat_lt['utilizacao']!=None:
                self.cb_lt_utilizacao.setCurrentText(self.dic_campos_lt['utilizacao'][feat_lt['utilizacao']])
            else:
                self.cb_lt_utilizacao.setCurrentText('')
    
    def getCamposUn(self):
        if self.cb_un_ids.currentText()!='':
            #self.setCamposUn()
            #apaga os combobox unidade
            self.cb_un_situacao_unidade.clear()
            self.cb_un_alinhamento.clear()
            self.cb_un_estrutura.clear()
            self.cb_un_paredes.clear()
            self.cb_un_revestimento.clear()
            self.cb_un_cobertura.clear()
            self.cb_un_tipo_edif.clear()
            self.cb_un_padrao_const.clear()
            self.cb_un_conservacao.clear()
            self.cb_un_outras_instalac.clear()
            self.cb_un_posicionamento.clear()
            
            #insere dominios campos un
            #if self.cb_un_situacao_unidade.currentText()!='':
            self.cb_un_situacao_unidade.insertItems(1,list(self.dic_campos_un['situacao_unidade'].values())+[''])
            #if self.cb_un_alinhamento.currentText()!='':
            self.cb_un_alinhamento.insertItems(1,list(self.dic_campos_un['alinhamento'].values())+[''])
            #if self.cb_un_estrutura.currentText()!='':
            self.cb_un_estrutura.insertItems(1,list(self.dic_campos_un['estrutura'].values())+[''])
            #if self.cb_un_paredes.currentText()!='':
            self.cb_un_paredes.insertItems(1,list(self.dic_campos_un['paredes'].values())+[''])
            #if self.cb_un_revestimento.currentText()!='':
            self.cb_un_revestimento.insertItems(1,list(self.dic_campos_un['revestimento_externo'].values())+[''])
            #if self.cb_un_cobertura.currentText()!='':
            self.cb_un_cobertura.insertItems(1,list(self.dic_campos_un['cobertura'].values())+[''])
            #if self.cb_un_tipo_edif.currentText()!='':   
            self.cb_un_tipo_edif.insertItems(1,list(self.dic_campos_un['tipo_edificacao'].values())+[''])
            #if self.cb_un_padrao_const.currentText()!='':   
            self.cb_un_padrao_const.insertItems(1,list(self.dic_campos_un['padrao_construtivo'].values())+[''])
            #if self.cb_un_conservacao.currentText()!='':  
            self.cb_un_conservacao.insertItems(1,list(self.dic_campos_un['conservacao'].values())+[''])
            #if self.cb_un_outras_instalac.currentText()!='':  
            self.cb_un_outras_instalac.insertItems(1,list(self.dic_campos_un['outras_instalacoes'].values())+[''])
            #if self.cb_un_posicionamento.currentText()!='':  
            self.cb_un_posicionamento.insertItems(1,list(self.dic_campos_un['posicionamento'].values())+[''])
            
            unidades = self.map_unidades.currentLayer()

            id_un = int(self.cb_un_ids.currentText())
            feat_un = unidades.getFeature(id_un)
            if feat_un['situacao_unidade']!=None:
                self.cb_un_situacao_unidade.setCurrentText(self.dic_campos_un['situacao_unidade'][feat_un['situacao_unidade']])
            else:
                self.cb_un_situacao_unidade.setCurrentText('')
            if feat_un['alinhamento']!=None:
                self.cb_un_alinhamento.setCurrentText(self.dic_campos_un['alinhamento'][feat_un['alinhamento']])
            else:
                self.cb_un_alinhamento.setCurrentText('')
            if feat_un['estrutura']!=None:
                self.cb_un_estrutura.setCurrentText(self.dic_campos_un['estrutura'][feat_un['estrutura']])
            else:
                self.cb_un_estrutura.setCurrentText('')
            if feat_un['paredes']!=None:
                self.cb_un_paredes.setCurrentText(self.dic_campos_un['paredes'][feat_un['paredes']])
            else:
                self.cb_un_paredes.setCurrentText('')
            if feat_un['revestimento_externo']!=None:
                self.cb_un_revestimento.setCurrentText(self.dic_campos_un['revestimento_externo'][feat_un['revestimento_externo']])
            else:
                self.cb_un_revestimento.setCurrentText('')
            if feat_un['cobertura']!=None:
                self.cb_un_cobertura.setCurrentText(self.dic_campos_un['cobertura'][feat_un['cobertura']])
            else:
                self.cb_un_cobertura.setCurrentText('')
            if feat_un['tipo_edificacao']!=None:
                self.cb_un_tipo_edif.setCurrentText(self.dic_campos_un['tipo_edificacao'][feat_un['tipo_edificacao']])
            else:
                self.cb_un_tipo_edif.setCurrentText('')
            if feat_un['padrao_construtivo']!=None:
                self.cb_un_padrao_const.setCurrentText(self.dic_campos_un['padrao_construtivo'][feat_un['padrao_construtivo']])
            else:
                self.cb_un_padrao_const.setCurrentText('')
            if feat_un['conservacao']!=None:
                self.cb_un_conservacao.setCurrentText(self.dic_campos_un['conservacao'][feat_un['conservacao']])
            else:
                self.cb_un_conservacao.setCurrentText('')
            if feat_un['outras_instalacoes']!=None:
                self.cb_un_outras_instalac.setCurrentText(self.dic_campos_un['outras_instalacoes'][feat_un['outras_instalacoes']])
            else:
                self.cb_un_outras_instalac.setCurrentText('')
            if feat_un['posicionamento']!=None:
                self.cb_un_posicionamento.setCurrentText(self.dic_campos_un['posicionamento'][feat_un['posicionamento']])
            else:
                self.cb_un_posicionamento.setCurrentText('')

    def getN(self,campo,dominio):
        n = None
        for ns in self.dic_campos_lt[campo].keys():
            if self.dic_campos_lt[campo][ns] == dominio:
                n = ns
                break
        return n
    
    def getNun(self,campo,dominio):
        n = None
        for ns in self.dic_campos_un[campo].keys():
            if self.dic_campos_un[campo][ns] == dominio:
                n = ns
                break
        return n
        
    def setCamposLT(self):
        
        lotes = self.map_lote.currentLayer()
        
        if self.line_id_lote.displayText()!='':
            lotes.startEditing()
            lote_id = int(self.line_id_lote.displayText())
            feat_lt = lotes.getFeature(lote_id)
            if self.cb_lt_ocupacao.currentText()!='':
                feat_lt['ocupacao'] = self.getN('ocupacao',self.cb_lt_ocupacao.currentText())
            if self.cb_lt_situacao.currentText()!='':
                feat_lt['situacao_lote'] = self.getN('situacao_lote',self.cb_lt_situacao.currentText())
            if self.cb_lt_classe.currentText()!='':
                feat_lt['classe'] = self.getN('classe',self.cb_lt_classe.currentText())
            if self.cb_lt_calcada.currentText()!='':
                feat_lt['calcada'] = self.getN('calcada',self.cb_lt_calcada.currentText())
            if self.cb_lt_utilizacao.currentText()!='':
                feat_lt['utilizacao'] = self.getN('utilizacao',self.cb_lt_utilizacao.currentText())
            lotes.updateFeature(feat_lt)
        lotes.commitChanges()
        
    
    
    def setCamposUn(self):
        unidades = self.map_unidades.currentLayer()
        
        if self.cb_un_ids.currentText()!='':
            unidades.startEditing()
            unidade_id = int(self.cb_un_ids.currentText())
            feat_un = unidades.getFeature(unidade_id)
            
            if self.cb_un_situacao_unidade.currentText()!='':
                feat_un['situacao_unidade'] = self.getNun('situacao_unidade',self.cb_un_situacao_unidade.currentText())
            if self.cb_un_alinhamento.currentText()!='':
                feat_un['alinhamento'] = self.getNun('alinhamento',self.cb_un_alinhamento.currentText())
            if self.cb_un_estrutura.currentText()!='':
                feat_un['estrutura'] = self.getNun('estrutura',self.cb_un_estrutura.currentText())
            if self.cb_un_paredes.currentText()!='':
                feat_un['paredes'] = self.getNun('paredes',self.cb_un_paredes.currentText())
            if self.cb_un_revestimento.currentText()!='':
                feat_un['revestimento_externo'] = self.getNun('revestimento_externo',self.cb_un_revestimento.currentText())
            if self.cb_un_cobertura.currentText()!='':
                feat_un['cobertura'] = self.getNun('cobertura',self.cb_un_cobertura.currentText())
            if self.cb_un_tipo_edif.currentText()!='':
                feat_un['tipo_edificacao'] = self.getNun('tipo_edificacao',self.cb_un_tipo_edif.currentText())
            if self.cb_un_padrao_const.currentText()!='':
                feat_un['padrao_construtivo'] = self.getNun('padrao_construtivo',self.cb_un_padrao_const.currentText())
            if self.cb_un_conservacao.currentText()!='':
                feat_un['conservacao'] = self.getNun('conservacao',self.cb_un_conservacao.currentText())
            if self.cb_un_outras_instalac.currentText()!='':
                feat_un['outras_instalacoes'] = self.getNun('outras_instalacoes',self.cb_un_outras_instalac.currentText())
            if self.cb_un_posicionamento.currentText()!='':
                feat_un['posicionamento'] = self.getNun('posicionamento',self.cb_un_posicionamento.currentText())
            unidades.updateFeature(feat_un)
        unidades.commitChanges()
        
    
    def fill_fcbs(self, mlcb, fcb):
        # print("fcb.objectName()= ", fcb.objectName())
        try:
            vlayer = mlcb.currentLayer()  # run method
            fcb.setLayer(vlayer)  # run method
            list_alias = self.dic_field_alias[fcb.objectName()]
            list_fields = vlayer.fields().names()
            for alias in list_alias:
                for field in list_fields:
                    if alias in field.lower():
                        fcb.setField(field)
        except:
            pass
    
    
    def close(self,visible):
        if not visible:
            print("close",visible)
            self.deletar_sinal()
        
    def changedMapUn(self):
        self.layer_un_spc_idx = None
        self.setupindex()
        
    def changeMapLt(self):
        self.layer_lt_spc_idx = None
        self.setupindex()
        
    def setupindex(self):
        self.lyr_un = self.map_unidades.currentLayer()
        self.lyr_lt = self.map_lote.currentLayer()
        if not self.layer_un_spc_idx:
            self.layer_un_spc_idx = QgsSpatialIndex(self.lyr_un.getFeatures())   
        if not self.layer_lt_spc_idx:
            self.layer_lt_spc_idx = QgsSpatialIndex(self.lyr_lt.getFeatures())

    def setRuber(self):
        self.rb_center.reset(QgsWkbTypes.PointGeometry)
        geom = QgsGeometry(QgsPoint(self.canvas.center()))
        self.rb_center.addGeometry(geom)
        
    def getLote(self,coord):
        print("get lote")
        self.lyr_lt = self.map_lote.currentLayer()
        nearests_lts = self.layer_lt_spc_idx.nearestNeighbor(coord, 3)
        point_geom = QgsGeometry(QgsPoint(coord))
        for lt in self.lyr_lt.getFeatures(nearests_lts):
            if lt.geometry().intersects(point_geom):
                if lt.id() != self.last_lote_id:
                    self.last_lote_id = lt.id()
                    print(lt.id())
                    self.line_id_lote.setText(str(lt.id()))
                    self.getUnidades(lt.id(),coord)
                    self.getCamposLT()
                    if self.line_password.displayText()!='' and self.check_foto.isChecked():
                        if self.connected:
                            self.getFotoFachadaRede(lt.id())
                            break
                        else:
                            self.connectDB()
                            break
                    break
                 
        
    def getUnidades(self,id_lote,coord):
        print("get unidades")
        self.lyr_un = self.map_unidades.currentLayer()
        ids_uns = []
        ids_uns_ = []
        self.lyr_un.removeSelection()
        nearest_uns = self.layer_un_spc_idx.nearestNeighbor(coord, 100)
        for un in self.lyr_un.getFeatures(nearest_uns):
            if un['id_lote'] == id_lote:
                ids_uns.append(str(un.id()))
                ids_uns_.append(un.id())
        self.lyr_un.select(ids_uns_)
        #self.line_id_un.setText(str(ids_uns))
        self.cb_un_ids.clear()
        self.cb_un_ids.insertItems(1,ids_uns)
        #self.setVerificado()
    
    def connectDB(self):
        if not self.connected:
            if self.line_password.displayText()!='':
                un = self.map_unidades.currentLayer()
                source_un = un.source()
                data1 = source_un[source_un.find('table=') + len('table='):source_un.find(" (geom)")].replace('"','').replace("'","").split('.')
                data2 = source_un[source_un.find('dbname=') + len('dbname='):source_un.find("host=")].replace('"','').replace(" ","").replace("'","").split('.')
                data3 = source_un[source_un.find('host=') + len('host='):source_un.find("port=")].replace('"','').replace(" ","").replace("'","")
                data4 = source_un[source_un.find('user=') + len('user='):source_un.find("password=")].replace('"','').replace(" ","").replace("'","")
                data5 = source_un[source_un.find('port=') + len('port='):source_un.find("user=")].replace('"','').replace(" ","").replace("'","")
                if(len(data1)==2):
                    self.esquema_un = data1[0]
                    self.tabela_un = data1[1]
                if(data2!=''):
                    self.db_name = data2[0]
                if(data3!=''):
                    self.host = data3
                if(data5!=''):
                    self.port = data5
                if(data4 != ''):
                    self.user = data4
                self.password = self.line_password.text()
                
                self.conn = psycopg2.connect(
                        database=self.db_name,
                        user=self.user,
                        password=self.password,
                        host=self.host,
                        port=self.port)
                        
                self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                self.connected = True
                print("conn", self.conn)
        else:
            pass
    
    def getFotoFachadaRede(self,id_lote):
        sql = f"select diretorio,nome_foto from foto_fachada.foto_fachada_arquivo where lote_id = {id_lote} limit 1"
        print(sql)
        self.cur.execute(sql)
        self.conn.commit()
        data = self.cur.fetchall()
        if(len(data)>0):
            for row in data:
                image = os.path.join(row[0].replace("\\ManausSt02\Projeto","\\bsbtopo09\Fotos_360_03"),row[1]+'.jpg') #
        else:
            image = 0
            
        
        image_1 = image #os.path.join(image.replace("\\ManausSt02\Projeto","\\bsbtopo09\Fotos_360_03")+'.jpg')

        if(image_1!=0):
            image_2 = Image.open(image_1)
            print("image_2 ok!", image_2)
        else:
            #image_2 = Image.open(tmppath_secretaria_logo)
            image_2 = 0
            print("image_2 not ok!", image_2)
            QMessageBox.information(None,"Erro ao abrir imagem", "Imagem selecionada não encontrada!")                
            pass
        
        if image_1 != 0:
            image_2 = image_2.convert('RGB')
            tmppath = "C:\\Users\\{}\\AppData\\Local\\Temp\\temp_img1234.jpeg".format(os.getlogin())
            image_2.save(tmppath,'JPEG')
            #image_2.show()
            
                
            # if (os.path.exists('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe')):
                # chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
                # webbrowser.get(chrome_path).open(tmppath)
                # print('link chrome1')
            # elif (os.path.exists('C:/Program Files/Google/Chrome/Application/chrome.exe')):
                # chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
                # webbrowser.get(chrome_path).open(tmppath)
                # print('link chrome2')
            
            # else:
            webbrowser.get('windows-default').open(tmppath)
            print('link_default')
        
    def getFotoFachada(self,id_lote):
        
        print("foto")
        #try:
        if 1:
            sql = f"select imagem from foto_fachada.foto_fachada_arquivo where lote_id = {id_lote} limit 1"
            print(sql)
            self.cur.execute(sql)
            self.conn.commit()
            data = self.cur.fetchall()

            if(len(data)>0):
       
                for row in data:
                    image = row[0]
            else:
            
                image = 0
            

            image_1 = image

            if(image_1!=0):
                image_3 = io.BytesIO(image_1)
                image_2 = Image.open(io.BytesIO(image_1))
                print("image_2 ok!", image_2)
            else:
                #image_2 = Image.open(tmppath_secretaria_logo)
                image_2 = 0
                print("image_2 not ok!", image_2)
                QMessageBox.information(None,"Erro ao abrir imagem", "Imagem selecionada não encontrada!")                
                pass
                
            if image_1 != 0:
                image_2 = image_2.convert('RGB')
                tmppath = "C:\\Users\\{}\\AppData\\Local\\Temp\\temp_img1234.jpeg".format(os.getlogin())
                image_2.save(tmppath,'JPEG')
                #image_2.show()
                
                    
                # if (os.path.exists('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe')):
                    # chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
                    # webbrowser.get(chrome_path).open(tmppath)
                    # print('link chrome1')
                # elif (os.path.exists('C:/Program Files/Google/Chrome/Application/chrome.exe')):
                    # chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
                    # webbrowser.get(chrome_path).open(tmppath)
                    # print('link chrome2')
                
                # else:
                webbrowser.get('windows-default').open(tmppath)
                print('link_default')
    
    
    
        #t = threading.Thread(target=open_url)
        #t.start()

    def sinal_mapa(self):
        coord = self.canvas.center()
        print(coord)
        self.getLote(coord)
    
    def unsetRuber(self):
        pass
    
    def criar_sinal(self):
        #Cria a conexão com o mapa
        try:
            self.canvas.zoomNextStatusChanged.disconnect(self.sinal_mapa)
            self.canvas.extentsChanged.disconnect(self.setRuber)
            #self.canvas.mouseMoveEvent = self.unsetRuber()
        except:
            self.canvas.zoomNextStatusChanged.connect(self.sinal_mapa)
            self.canvas.extentsChanged.connect(self.setRuber)
            #self.canvas.mouseMoveEvent = self.setRuber()
            #self.setStyleSheet("QDockWidget#"+str(self.objectName())+"::title {background-color:lightgreen}")
            self.wd.setStyleSheet('background-color: rgb(185,249,213)')
            self.rb_center.reset(QgsWkbTypes.PointGeometry)
            geom = QgsGeometry(QgsPoint(self.canvas.center()))
            self.rb_center.addGeometry(geom)
        
        if not self.connectDB:
            self.connectDB()
        
        return True
            
    
    def deletar_sinal(self):
        try:
            self.canvas.zoomNextStatusChanged.disconnect(self.sinal_mapa)
            self.canvas.extentsChanged.disconnect(self.setRuber)
            #self.canvas.mouseMoveEvent = self.unsetRuber()
            #self.setStyleSheet("QDockWidget#"+str(self.objectName())+"::title {background-color:lightred}")
            self.wd.setStyleSheet('background-color: rgb(255,170,170)')
            self.rb_center.reset(QgsWkbTypes.PointGeometry)
            self.connected = False
            try:
                self.conn.close()
                self.cur.close()
                print("desconectou")
            except:
                print("problema ao desconectar")
                pass
        except:
            pass
        return False
try:
    self.verificacao.ObjectName()
    #self.addDockWidget(Qt.RightDockWidgetArea, self.verificacao)
    print("achou!",self.verificacao)
except:
    self.sinal_status = False
    self.verificacao = Verificacao(self)
   # self.addDockWidget(Qt.RightDockWidgetArea,self.verificacao)
    #self.verificacao.show()
    print("nao achou, criado!",self.verificacao)