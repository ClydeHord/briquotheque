# © 2026 Clýde Hørd (ClydeHord sur GitHub) — auteur de Briquothèque · source : https://github.com/ClydeHord/briquotheque · licence : LICENCE (mention à conserver)
"""Détourage par ISNet (modèle libre « isnet-general-use », onnxruntime, sur ce serveur : la photo ne part nulle part).

Lancé par server.py dans un processus à part, une photo à la fois : le modèle (~180 Mo) n'occupe la mémoire (~810 Mo au pic)
que pendant le détourage, puis tout est libéré. Ce script tourne avec un Python qui a onnxruntime, numpy et pillow
(environnement à part, voir BQ_CUTOUT_PY dans server.py).

Usage : python detourage.py <modele.onnx> <photo d'entrée> <sortie .png> [mask]
Sortie : la photo, fond remplacé par du blanc (comme le détourage sur l'appareil), mêmes dimensions.
"""
import os
import sys

import numpy as np
import onnxruntime as ort
from PIL import Image


def main(model, src, dst, mode="photo"):
    so = ort.SessionOptions()
    so.enable_cpu_mem_arena = False   # pas de réserve mémoire : ~810 Mo au pic au lieu de bien plus
    so.intra_op_num_threads = os.cpu_count() or 1   # mesuré le 15/11 : sur 1 cœur, 1 fil est le plus rapide (7,8 s contre 8,5 s à 2 fils)
    sess = ort.InferenceSession(model, so, providers=["CPUExecutionProvider"])
    im = Image.open(src).convert("RGB")
    x = np.asarray(im.resize((1024, 1024), Image.LANCZOS), dtype=np.float32) / 255.0 - 0.5   # ISNet : entrée 1024², moyenne 0,5
    out = sess.run(None, {sess.get_inputs()[0].name: x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0, 0]
    m = (out - out.min()) / (out.max() - out.min() + 1e-8)   # probabilité « objet » 0-1
    mask = Image.fromarray((m * 255).astype(np.uint8)).resize(im.size, Image.LANCZOS)
    if mode == "mask":   # seulement le masque (gris : blanc = objet) ; l'appli l'applique à la photo en pleine taille
        mask.save(dst, "PNG")
        return
    Image.composite(im, Image.new("RGB", im.size, "white"), mask).save(dst, "PNG")


if __name__ == "__main__":
    main(*sys.argv[1:5])
