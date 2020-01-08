#ifndef CANVAS_H
#define CANVAS_H

#include <QWidget>
#include <QKeyEvent>

class Canvas : public QWidget {
private:
	static enum { MODE_HORIZONTAL = 0, MODE_VERTICAL };

private:
	QImage orig_image;
	QImage image;
	std::vector<float> floorParams;
	std::vector<std::pair<int, float>> columnParams;
	int mode;

	bool ctrlPressed;
	bool shiftPressed;
	
public:
	Canvas(QWidget *parent = NULL);
	
protected:
	void paintEvent(QPaintEvent *event);
	void mousePressEvent(QMouseEvent* e);
	void resizeEvent(QResizeEvent *e);

public:
	void setFloorParams(const std::vector<float>& params) { this->floorParams = params; }
	void setColumnParams(const std::vector<std::pair<int, float>>& params) { this->columnParams = params; }
	std::vector<float> getFloorParams() { return floorParams; }
	std::vector<std::pair<int, float>> getColumnParams() { return columnParams; }
	void loadImage(const QString& filename);
	void undo();
	void setModeHorizontal();
	void setModeVertical();
	void keyPressEvent(QKeyEvent* e);
	void keyReleaseEvent(QKeyEvent* e);
};

#endif // CANVAS_H
