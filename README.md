# Life Assistant
生活小助手，使用python编写的一些小工具用于提高生活效率。  
目前主要包括了:
- social_security 社保查询(苏州工业园区社保缴费记录查询)  

#USAGE:
-  sipss.py (苏州园区社保查询程序)  

    通过设置 [config.cfg](life_assistant/config.cfg)  查询
    ```Bash     
    $ > sipps.py 
    ```
    通过命令行参数
    ```Bash
    $ > sipss.py <username> <password> [--m=email]
    ```
# INSTALL
- **sipss.py**  
    Prerequisites:
    - Python 3
    - [Tesseract](https://github.com/tesseract-ocr/tesseract)
    - nodejs
    - PIL  
    
    安装python依赖包: 
    ``` 
    $ (env)> pip install requests pil pytesseract prettytable
    ```
    
    安装sipss:
    ```
    $ > git clone git@github.com:fan-qiang/life_assistant.git
    ```
    