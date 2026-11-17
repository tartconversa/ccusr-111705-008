"""本地业务页面交互。"""

def detail_fragment(item):
    return '<button id="gallery-next">下一张素材</button><img id="material" alt="联名商品图" src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="><output id="gallery-state">封面</output><a id="license" href="/detail?id=ip-02">授权说明</a><script>document.querySelector(\'#gallery-next\').onclick=()=>{document.querySelector(\'#gallery-state\').textContent=\'加载中\';setTimeout(()=>document.querySelector(\'#gallery-state\').textContent=\'规格素材\',50)};</script>'
