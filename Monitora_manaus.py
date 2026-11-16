# -*- coding: utf-8 -*-
import os
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QComboBox
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsCoordinateTransform
)

from .Monitora_manaus_dialog import MonitoraManausDialog


class MonitoraManaus:
    """Plugin QGIS Monitora Manaus - Consulta e Filtragem de Câmeras."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            f'MonitoraManaus_{locale}.qm'
        )
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Monitora Manaus')
        self.dlg = None

    def tr(self, message):
        return QCoreApplication.translate('MonitoraManaus', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None
    ):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Monitora Manaus'),
            callback=self.run,
            parent=self.iface.mainWindow()
        )

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&Monitora Manaus'), action)
            self.iface.removeToolBarIcon(action)

    def buscar_camada_existente(self):
        """Verifica se a camada de câmeras já está no projeto atual."""
        nomes = ["pontos cameras", "pontos_cameras", "Câmeras - Centro de Manaus", "cameras_manaus"]
        for camada in QgsProject.instance().mapLayers().values():
            if isinstance(camada, QgsVectorLayer) and (
                camada.name() in nomes or "cameras_manaus.gpkg" in camada.source()
            ):
                return camada
        return None

    def definir_visibilidade(self, camada, visivel):
        """Liga ou desliga a visualização da camada no painel Camadas."""
        if camada is not None:
            no = QgsProject.instance().layerTreeRoot().findLayer(camada.id())
            if no is not None:
                no.setItemVisibilityChecked(visivel)

    def centralizar_na_camada(self, camada):
        """Enquadra o mapa nos pontos filtrados."""
        try:
            canvas = self.iface.mapCanvas()
            extensao = camada.extent()
            if not extensao.isEmpty():
                transform = QgsCoordinateTransform(
                    camada.crs(),
                    canvas.mapSettings().destinationCrs(),
                    QgsProject.instance()
                )
                extensao_mapa = transform.transformBoundingBox(extensao)
                extensao_mapa.scale(1.2)
                canvas.setExtent(extensao_mapa)
                canvas.refresh()
        except Exception:
            pass

    def encontrar_campo(self, camada, palavra_chave):
        """Encontra o nome real da coluna no GeoPackage."""
        for campo in camada.fields():
            if palavra_chave in campo.name().lower():
                return campo.name()
        return None

    def run(self):
        """Exibe apenas os filtros e mostra os pontos existentes após clicar em OK."""
        try:
            # 1. Mantém os pontos ocultos enquanto o usuário escolhe os filtros
            camada = self.buscar_camada_existente()
            if camada is not None:
                self.definir_visibilidade(camada, False)

            # 2. Monta a janela com a opção 'Todas' no início de cada lista
            if self.dlg is None:
                self.dlg = MonitoraManausDialog()
                for combo in self.dlg.findChildren(QComboBox):
                    itens = [combo.itemText(i) for i in range(combo.count())]
                    if "Todas" not in itens:
                        combo.insertItem(0, "Todas")

            for combo in self.dlg.findChildren(QComboBox):
                combo.setCurrentIndex(0)

            resultado = self.dlg.exec_()

            # 3. Somente após clicar em OK, carrega e filtra os pontos existentes
            if resultado:
                combos = sorted(
                    self.dlg.findChildren(QComboBox),
                    key=lambda w: (w.y() // 30, w.x())
                )

                if camada is None:
                    gpkg_path = os.path.join(self.plugin_dir, 'cameras_manaus.gpkg')
                    if not os.path.exists(gpkg_path):
                        self.iface.messageBar().pushWarning(
                            "Monitora Manaus",
                            "Arquivo 'cameras_manaus.gpkg' não encontrado na pasta do plugin."
                        )
                        return

                    camada = QgsVectorLayer(gpkg_path, "Câmeras - Centro de Manaus", "ogr")
                    if not camada.isValid():
                        self.iface.messageBar().pushCritical(
                            "Monitora Manaus",
                            "Não foi possível ler o arquivo 'cameras_manaus.gpkg'."
                        )
                        return
                    adicionada_agora = True
                else:
                    adicionada_agora = False

                # Protege a camada como somente leitura para ninguém alterar seus dados pelo plugin
                camada.setReadOnly(True)

                # Aplica o filtro escolhido nos 3 botões
                filtros = []
                chaves = ['esfera', 'tipo', 'lgpd']

                for idx, chave in enumerate(chaves):
                    if idx < len(combos):
                        valor = combos[idx].currentText().strip()
                        nome_campo = self.encontrar_campo(camada, chave)
                        if nome_campo and valor and valor.lower() not in ("todas", "todos", ""):
                            valor_seguro = valor.replace("'", "''")
                            filtros.append(f"TRIM(\"{nome_campo}\") = '{valor_seguro}'")

                camada.setSubsetString(" AND ".join(filtros))

                if adicionada_agora:
                    QgsProject.instance().addMapLayer(camada)

                self.definir_visibilidade(camada, True)
                camada.triggerRepaint()
                self.centralizar_na_camada(camada)

                total = camada.featureCount()
                self.iface.messageBar().pushSuccess(
                    "Monitora Manaus",
                    f"Consulta concluída: {total} câmera(s) encontrada(s)."
                )

        except Exception as erro:
            self.iface.messageBar().pushCritical(
                "Monitora Manaus",
                f"Erro ao executar: {str(erro)}"
            )