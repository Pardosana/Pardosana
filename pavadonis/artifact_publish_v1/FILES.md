# artifact_publish_v1: precīzs failu saraksts

Kontrolsummas attiecas uz šo commit (LF rindu beigas, skat. `pavadonis/.gitattributes`).
`FILES.md` pats sarakstā nav iekļauts.

| Fails | Izvieto Office PC | Baiti | SHA256 |
|---|---|---|---|
| `artifact_publish_v1/__init__.py` | jā | 813 | `0ffac434e18a343479026ca81f9809f101d1f05de91f368484caff1ed9e2b171` |
| `artifact_publish_v1/adapter.py` | jā | 13347 | `63d9fa07c9c776badd89ad61294ccff8045bf7cf7aa4d62c0938f8cd2693026b` |
| `artifact_publish_v1/drive.py` | jā | 5353 | `7a1ef6da9ac8f65644b85b2c438a494bdb89648469d2de79cd93fbdd0f79a7ac` |
| `artifact_publish_v1/config.example.json` | kā šablons → konfigurācija | 258 | `83b72868c10b292f723173f09a39c1323c49cd1bce4dee0ce195cfeb28ca098f` |
| `artifact_publish_v1/INSTALL.md` | nē (dokumentācija) | 7157 | `e1c594010ead39908e02319e5943c32488ea88f015f3003b7a90863ab30ca2f4` |
| `artifact_publish_v1/ROLLBACK.md` | nē (dokumentācija) | 1289 | `8be9ef4604d6ee0266ccaf50800ed796398a3d9e4b4ea2d795401197ad21fec9` |
| `artifact_publish_v1/tests/__init__.py` | nē (tikai testiem) | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `artifact_publish_v1/tests/test_adapter.py` | nē (tikai testiem) | 8639 | `b1c9f69d96a21b2597cc3268c01d5624d45099d7c789d2b1870f16a3dc104cc4` |
| `artifact_publish_v1/tests/test_drive_client.py` | nē (tikai testiem) | 3340 | `f7394cfe4789380ad1851ccd7926132ae99e12dcb7e33aac803149a8490f6068` |

PAVADONIS pusē mainās tikai `production_worker.py` (`ProductionWorker.__init__()` reģistrācijas bloks, skat. INSTALL.md 2. sadaļu) un tiek pievienots viens konfigurācijas JSON.
