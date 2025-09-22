# 图片EXIF时间水印添加工具

这是一个Python命令行工具，用于读取图片的EXIF信息中的拍摄时间，并将其作为水印添加到图片上。

## 功能特点

- 读取图片EXIF信息中的拍摄时间（年月日）
- 支持自定义水印字体大小、颜色和位置
- 批量处理指定目录下的所有图片
- 将处理后的图片保存到新目录中

## 安装依赖

在使用本工具前，请确保已安装以下依赖库：

```bash
pip install pillow
```

## 使用方法

基本用法：

```bash
python watermark.py [图片目录路径] [选项]
```

### 参数说明

- `图片目录路径`：必选参数，指定包含图片的目录路径

### 可选参数

- `--size SIZE`：设置水印字体大小（默认：20）
- `--color COLOR`：设置水印颜色（默认：white）
- `--position POSITION`：设置水印位置（默认：bottom-right）

### 支持的水印位置

- `top-left`：左上角
- `top-center`：上方居中
- `top-right`：右上角
- `center-left`：左侧居中
- `center`：正中央
- `center-right`：右侧居中
- `bottom-left`：左下角
- `bottom-center`：下方居中
- `bottom-right`：右下角

### 示例

```bash
# 使用默认设置
python watermark.py D:\Photos

# 自定义水印设置
python watermark.py D:\Photos --size 24 --color red --position top-right
```

## 输出

程序会在指定的图片目录下创建一个新的子目录，命名为"原目录名_watermark"，并将添加水印后的图片保存到该目录中。

## 注意事项

- 程序仅处理具有EXIF拍摄时间信息的图片
- 支持的图片格式包括：JPG、JPEG、PNG、TIFF、BMP
- 水印颜色可以使用颜色名称（如red、blue）或十六进制颜色代码（如#FF0000）

## 错误处理

- 如果指定的目录不存在，程序会显示错误信息并退出
- 如果目录中没有图片文件，程序会显示提示信息并退出
- 如果图片没有EXIF信息或无法提取拍摄日期，程序会跳过该图片并继续处理其他图片