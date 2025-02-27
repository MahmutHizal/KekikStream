# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from KekikStream.CLI  import konsol
from asyncio          import run
from KekikStream.Core import PluginManager, ExtractorManager, MediaManager, MovieInfo, SeriesInfo

async def main():
    plugins = PluginManager()
    ext     = ExtractorManager()
    media   = MediaManager()

    for eklenti_adi in plugins.get_plugin_names():
        konsol.log(f"[red]Eklenti     » [purple]{eklenti_adi}")
        plugin = plugins.select_plugin(eklenti_adi)

        if not plugin.main_page:
            continue

        konsol.log(f"[red]main_url    » [purple]{plugin.main_url}")
        konsol.log(f"[red]favicon     » [purple]{plugin.favicon}")
        konsol.log(f"[red]description » [purple]{plugin.description}")

        for url, category in plugin.main_page.items():
            konsol.log(f"[red]Kategori    » [purple]{category:<12} » {url}")
            icerikler = await plugin.get_main_page(1, url, category)

            for icerik in icerikler:
                konsol.log(icerik)

                detay = await plugin.load_item(icerik.url)
                konsol.log(detay)

                if isinstance(detay, MovieInfo):
                    konsol.log(f"[red]Film        » [purple]{detay.title}")
                    icerikler = await plugin.load_links(detay.url)
                elif isinstance(detay, SeriesInfo):
                    konsol.log(f"[red]Dizi        » [purple]{detay.title}")
                    bolum     = detay.episodes[0]
                    icerikler = await plugin.load_links(bolum.url)

                for link in icerikler:
                    konsol.log(f"[red]icerik_link » [purple]{link}")

                    if hasattr(plugin, "play") and callable(getattr(plugin, "play", None)):
                        data = plugin._data.get(link, {})
                        await plugin.play(
                            name      = data.get("name"),
                            url       = link,
                            referer   = data.get("referer"),
                            subtitles = data.get("subtitles")
                        )
                    elif extractor := ext.find_extractor(link):
                        sonuc = await extractor.extract(link, referer=plugin.main_url)
                        konsol.log(sonuc)
                        media.set_title(f"{sonuc.name} - {plugin.name} - {detay.title} - {bolum.title or f'{bolum.season}x{bolum.episode}'}")
                        media.play_media(sonuc)
                    else:
                        konsol.print(f"[red]Önerilen araç bulunamadı: {link}")

                    break
                break
            break

if __name__ == "__main__":
    run(main())