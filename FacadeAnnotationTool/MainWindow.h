#pragma once

#include <QtWidgets/QMainWindow>
#include "ui_MainWindow.h"
#include "Canvas.h"
#include <QFileInfoList>

class MainWindow : public QMainWindow
{
    Q_OBJECT

private:
	Ui::MainWindowClass ui;
	Canvas* canvas;
	QFileInfoList fileInfoList;
	int curIndex;
	QMap<QString, std::vector<float>> all_floor_params;
	QMap<QString, std::vector<std::pair<int, float>>> all_column_params;

public:
    MainWindow(QWidget *parent = Q_NULLPTR); 

	void loadImage(const QFileInfo& fileinfo);
	void loadFloorParams();
	void loadColumnParams();
	void saveFloorParams();
	void saveColumnParams();

public slots:
	void onOpen();
	void onSave();
	void onNext();
	void onPrevious();
	void onUndo();
	void onModeChanged();
};
