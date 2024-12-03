# Troubleshooting

Typical issues that users\developers can have

## SystemError

**import xmlsec - SystemError: null argument to internal routine**

If this error appears on CentOS, you might need to install
additional packages:

    ```
    yum install libxml2-devel xmlsec1-devel xmlsec1-openssl-devel libtool-ltdl-devel
    ```
