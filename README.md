## 配置说明
- mysql配置
- sqlmap配置
1. SQLMAP_LIMIT_RUN，限制sqlmap跑的进程数
2. SQLMAP_REQUESTFILE_PATH：保存数据包的位置
3. SQLMAP_PARMEXCLUDE：排除的参数（level3以上）
4. SQLMAP_API_SERVER：连接sqlmapapi，需要多开，因为sqlmap多了之后，一个api服务器跑不动，会死掉

- 代理配置
1. EXCLUDE_STATIC_FILE：排除静态文件
- fortify配置
1. fortify_path：保存源码位置
2. report_path：保存报告的位置
3. filter_title：过滤高危的漏洞，比如sql注入，xss
- gitlab配置
1. git_api_choice：有两种选择，1，本地文件，里面都写了要扫描的github地址（推荐）; 2,接口模式，请求网站获取扫描地址。
2. git_address：项目地址列表
3. GIT_ADDRESS:模式2，接口地址
4. GIT_PARM：模式2，json参数,例如{"giturl":[1,2,3,4]}