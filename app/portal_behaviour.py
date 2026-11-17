"""本地业务页面交互。"""
import json
from html import escape

DEFAULT_VARIANTS = ['红色款', '蓝色款']

def variants_of(item):
    return item.get('variants') or DEFAULT_VARIANTS

def material_variants(item):
    return item.get('material_variants') or variants_of(item)

def license_variants(item):
    return item.get('license_variants') or variants_of(item)

def detail_fragment(item):
    options = ''.join(f'<option>{escape(variant)}</option>' for variant in variants_of(item))
    return ("<button id=\"gallery-next\">下一张素材</button><img id=\"material\" alt=\"联名商品图\" src=\"data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=\"><output id=\"gallery-state\">封面</output><a id=\"license\" href=\"/detail?id=ip-02\">授权说明</a>"
            f"<select id=\"variant\">{options}</select><button id=\"revoke\">模拟授权撤回</button>"
            "<script>let variant=document.querySelector('#variant'),gallery=document.querySelector('#gallery-state'),license=document.querySelector('#license');let revoked=false;variant.onchange=()=>{gallery.textContent='等待素材';license.textContent=variant.value+'：'+(revoked?'授权撤回':'授权说明')};document.querySelector('#gallery-next').onclick=()=>{let selected=variant.value;gallery.textContent='加载中';setTimeout(()=>gallery.textContent=selected+'：规格素材',50)};document.querySelector('#revoke').onclick=()=>{revoked=true;license.textContent=variant.value+'：授权撤回'};</script>")

def source_extension(item):
    variants = variants_of(item)
    initial = variants[0]
    revoked = bool(item.get('license_revoked'))
    external = json.dumps(item.get('license_external') or None, ensure_ascii=False)
    start_revision = 2 if revoked else 1
    cover = f'{initial}：素材授权待复核' if revoked else '封面待核'
    return f"""<output id="material-revision" data-variant="{escape(initial)}" data-product="{escape(item['id'])}" data-revision="{start_revision}">{escape(cover)}</output><output id="license-revision"></output><script>(()=>{{
let material=document.querySelector('#material-revision'),license=document.querySelector('#license-revision'),variant=document.querySelector('#variant');
let revision={start_revision},image=document.querySelector('#material'),link=document.querySelector('#license');
const external={external};
const source=()=>'/material?product='+encodeURIComponent(material.dataset.product)+'&variant='+encodeURIComponent(variant.value)+'&revision='+revision;
const licenseSource=()=>external||('/license?product='+encodeURIComponent(material.dataset.product)+'&variant='+encodeURIComponent(variant.value)+'&revision='+revision);
if({json.dumps(not revoked)}){{image.src=source();link.href=licenseSource();}}else{{image.removeAttribute('src');link.removeAttribute('href');license.textContent=variant.value+'：授权已撤回';}}
variant.addEventListener('change',()=>{{revision++;material.dataset.variant=variant.value;material.dataset.revision=revision;material.textContent='等待素材';license.textContent='';image.removeAttribute('src');link.href=licenseSource();}});
document.querySelector('#gallery-next').addEventListener('click',()=>{{let selected=variant.value,viewed=revision;material.textContent='素材加载中';setTimeout(()=>{{material.textContent=selected+'：本地素材版本 '+viewed;image.src=source();}},75)}});
link.addEventListener('click',()=>{{license.textContent=variant.value+'：授权说明版本 '+revision;}});
document.querySelector('#revoke').addEventListener('click',()=>{{revision++;material.dataset.revision=revision;material.textContent=variant.value+'：素材授权待复核';license.textContent=variant.value+'：授权已撤回';image.removeAttribute('src');link.removeAttribute('href');}});
}})();</script>"""
