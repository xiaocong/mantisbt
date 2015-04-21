Install
=======

    $ [sudo] apt-get install python-pip
    $ [sudo] pip install -r requirements.txt

How to use
==========

# 将ticket状态改为Resolve状态(缺省code为80)

    python mantis.py --wsdl="http://mantis.xxx.xxx/api/soap/mantisconnect.php?wsdl" --username=username --password=password --comment="在版本号xx.xx.xx修正本问题。" resolve 1234 1235 1236

# 给ticket增加comment

    python mantis.py --wsdl="http://mantis.xxx.xxx/api/soap/mantisconnect.php?wsdl" --username=username --password=password comment "本ticket以及被gerrit changeid http://gerrit.xxx.xxx/change/xxxxx 所修正." 1234 1234

References
==========

- [mantis api](http://mantishub.readthedocs.org/api.html)
- [mantis wsdl](http://mantis.smartisan.cn/api/soap/mantisconnect.php?wsdl)
- [pysimplesoap](https://code.google.com/p/pysimplesoap/wiki/SoapClient)