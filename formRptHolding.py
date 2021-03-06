# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, QtGui
import portfolio
import DataFrameModel as dfm
import datetime


class Ui_ReportHolding(object):
    def initUI(self, Ui_ReportHolding):

        self.acctList = ('CITIC', 'CMS', 'HUATAI', 'FUTU','SNOWBALL')
        self.initForm()

    def initForm(self):

        mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(mainLayout)

        self.Date = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.Date.setCalendarPopup(True)
        self.Date.setMaximumDate(QtCore.QDate.currentDate())
        self.Acct = QtWidgets.QComboBox()
        self.Acct.addItem('ALL')
        self.Acct.addItems(self.acctList)
        self.Region = QtWidgets.QComboBox()
        self.Region.addItems(['ALL', 'CHINA', 'HKSAR'])
        self.Region.setCurrentIndex(1)
        labelDate = QtWidgets.QLabel('Report Date')
        labelAcct = QtWidgets.QLabel('Account')
        labelRegion = QtWidgets.QLabel('Region')
        self.labelTime = QtWidgets.QLabel('')
        btnReport = QtWidgets.QPushButton("RUN REPORT")
        btnReport.clicked.connect(self.loadReport)
        hLayout = QtWidgets.QHBoxLayout()
        hLayout.addWidget(labelDate)
        hLayout.addWidget(self.Date)
        hLayout.addWidget(labelAcct)
        hLayout.addWidget(self.Acct)
        hLayout.addWidget(labelRegion)
        hLayout.addWidget(self.Region)
        hLayout.addStretch()
        hLayout.addWidget(self.labelTime)
        hLayout.addWidget(btnReport)
        mainLayout.addLayout(hLayout)

        self.MV_CNY = QtWidgets.QLabel('0.00')
        self.PL_CNY = QtWidgets.QLabel('0.00')
        self.MV_HKD = QtWidgets.QLabel('0.00')
        self.PL_HKD = QtWidgets.QLabel('0.00')
        label_MV_CNY = QtWidgets.QLabel('人民币市值')
        label_PL_CNY = QtWidgets.QLabel('人民币盈利')
        label_MV_HKD = QtWidgets.QLabel('港币市值')
        label_PL_HKD = QtWidgets.QLabel('港币盈利')
        gridEdit = QtWidgets.QGridLayout()
        gridEdit.addWidget(label_MV_CNY, 0, 0)
        gridEdit.addWidget(self.MV_CNY, 1, 0)
        gridEdit.addWidget(label_PL_CNY, 0, 1)
        gridEdit.addWidget(self.PL_CNY, 1, 1)
        gridEdit.addWidget(label_MV_HKD, 0, 2)
        gridEdit.addWidget(self.MV_HKD, 1, 2)
        gridEdit.addWidget(label_PL_HKD, 0, 3)
        gridEdit.addWidget(self.PL_HKD, 1, 3)
        gridEdit.setRowStretch(0, 1)
        gridEdit.setRowStretch(1, 1)
        groupBox = QtWidgets.QGroupBox('')
        groupBox.setLayout(gridEdit)
        mainLayout.addWidget(groupBox)

        self.tableHold = QtWidgets.QTableView()
        mainLayout.addWidget(self.tableHold)

        self.tableSector = QtWidgets.QTableView()
        mainLayout.addWidget(self.tableSector)

        mainLayout.setStretchFactor(hLayout, 1)
        mainLayout.setStretchFactor(groupBox, 1)
        mainLayout.setStretchFactor(self.tableHold, 12)
        mainLayout.setStretchFactor(self.tableSector, 3)

        for row in range(gridEdit.rowCount()):
            for column in range(gridEdit.columnCount()):
                item = gridEdit.itemAtPosition(row, column)
                if item is not None:
                    widget = item.widget()
                    widget.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                    if row == 1:
                        widget.setFont(QtGui.QFont("Timers", 20, QtGui.QFont.Bold))

        groupBox.setStyleSheet('''
            QGroupBox{border: 1px solid gray; background-color: white}
            ''')
        mainLayout.setSpacing(3)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        gridEdit.setContentsMargins(0, 0, 0, 0)
        hLayout.setContentsMargins(0, 0, 0, 0)

    def loadReport(self):

        self.labelTime.setText('')

        acct = self.Acct.currentText()
        if acct == 'ALL':
            strAcct = str(self.acctList)
        else:
            strAcct = acct

        dfHold = portfolio.get_hold(self.Date.date().toString('yyyy-MM-dd'), strAcct, self.Region.currentText())
        dfHold = dfHold.sort_values('SymbolCode', ascending=True)

        model = dfm.PandasModel(dfHold)
        self.tableHold.setModel(model)
        dfm.FormatView(self.tableHold)
        self.tableHold.sortByColumn(0, QtCore.Qt.AscendingOrder)

        self.load_sum_factor(dfHold)
        self.load_sector(dfHold)

        self.labelTime.setText(datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'))

    def load_sum_factor(self, dfHold):
        df = dfHold[['Cur', 'MV', 'PL']]
        df_sum = df.groupby(['Cur']).sum()

        if 'HKD' not in list(df_sum.index):
            df_sum.loc['HKD'] = [0, 0]

        if 'CNY' not in list(df_sum.index):
            df_sum.loc['CNY'] = [0, 0]

        self.MV_CNY.setText(format(df_sum.loc['CNY', 'MV'], '0,.2f'))
        self.PL_CNY.setText(format(df_sum.loc['CNY', 'PL'], '0,.2f'))
        self.MV_HKD.setText(format(df_sum.loc['HKD', 'MV'], '0,.2f'))
        self.PL_HKD.setText(format(df_sum.loc['HKD', 'PL'], '0,.2f'))

        if df_sum.loc['HKD', 'PL'] < 0:
            self.PL_HKD.setStyleSheet("color:red;")
        else:
            self.PL_HKD.setStyleSheet("color:black;")

        if df_sum.loc['CNY', 'PL'] < 0:
            self.PL_CNY.setStyleSheet("color:red;")
        else:
            self.PL_CNY.setStyleSheet("color:black;")

        # 解决QLabel setText不即时生效的问题
        self.MV_CNY.repaint()

    def load_sector(self, dfHold):
        dfSector = dfHold[['Sector', 'MV_CNY']]
        dfSum = dfSector.groupby(['Sector']).sum()
        total = dfSector[['MV_CNY']].sum()
        dfSum['Ratio'] = dfSum.apply(lambda x: round(x['MV_CNY']/total, 4), axis=1)
        dfSum.sort_values(by="Ratio", ascending=False, inplace=True)
        dfSum.loc['合计'] = [float(total), 1]
        dfSum['MV_CNY'] = dfSum.apply(lambda x: format(x['MV_CNY'], '0,.2f'), axis=1)
        dfSum['Ratio'] = dfSum.apply(lambda x: format(x['Ratio'], '.2%'), axis=1)
        df = dfSum.T

        model = QtGui.QStandardItemModel()
        dfm.load_table(self.tableSector, model, df)
