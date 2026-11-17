"""本地业务页面交互。"""

def detail_fragment(item):
    return "<button id=\"gallery-next\">下一张素材</button><img id=\"material\" alt=\"联名商品图\" src=\"data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=\"><output id=\"gallery-state\">封面</output><a id=\"license\" href=\"/detail?id=ip-02\">授权说明</a><select id=\"variant\"><option>红色款</option><option>蓝色款</option></select><button id=\"revoke\">模拟授权撤回</button><script>let variant=document.querySelector('#variant'),gallery=document.querySelector('#gallery-state'),license=document.querySelector('#license');let revoked=false;variant.onchange=()=>{gallery.textContent='等待素材';license.textContent=variant.value+'：'+(revoked?'授权撤回':'授权说明')};document.querySelector('#gallery-next').onclick=()=>{let selected=variant.value;gallery.textContent='加载中';setTimeout(()=>gallery.textContent=selected+'：规格素材',50)};document.querySelector('#revoke').onclick=()=>{revoked=true;license.textContent=variant.value+'：授权撤回'};</script>"

def source_extension(item):
    return f"""<output id="material-revision" data-variant="红色款" data-product="{item['id']}">封面待核</output><output id="license-revision"></output><script>(()=>{{
let material=document.querySelector('#material-revision'),license=document.querySelector('#license-revision'),variant=document.querySelector('#variant');
let revision=1,image=document.querySelector('#material'),link=document.querySelector('#license');
const source=()=>'/material?product='+encodeURIComponent(material.dataset.product)+'&variant='+encodeURIComponent(variant.value)+'&revision='+revision;
const licenseSource=()=>'/license?product='+encodeURIComponent(material.dataset.product)+'&variant='+encodeURIComponent(variant.value)+'&revision='+revision;
image.src=source();link.href=licenseSource();
variant.addEventListener('change',()=>{{revision++;material.dataset.variant=variant.value;material.textContent='等待素材';license.textContent='';image.removeAttribute('src');link.href=licenseSource();}});
document.querySelector('#gallery-next').addEventListener('click',()=>{{let selected=variant.value,viewed=revision;material.textContent='素材加载中';setTimeout(()=>{{material.textContent=selected+'：本地素材版本 '+viewed;image.src=source();}},75)}});
link.addEventListener('click',()=>{{license.textContent=variant.value+'：授权说明版本 '+revision;}});
document.querySelector('#revoke').addEventListener('click',()=>{{revision++;material.textContent=variant.value+'：素材授权待复核';license.textContent=variant.value+'：授权已撤回';image.removeAttribute('src');link.removeAttribute('href');}});
}})();</script>"""
