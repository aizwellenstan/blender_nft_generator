# Purpose:
# This file goes through all batches, renames, and sorts all nft files to a Complete_Collection folder in Aiz_Blender_NFT

import bpy
import os
import copy
import json
import shutil
import importlib
import requests
from os import listdir
from os.path import isfile, join
import json
import time

from . import Metadata

importlib.reload(Metadata)

removeList = [".gitignore", ".DS_Store"]


def getNFType(nftBatch_save_path):
    images = False
    animations = False
    models = False
    metaData = False

    batch1 = [x for x in os.listdir(nftBatch_save_path) if (x not in removeList)][0]  # Gets first Batch and ignores removeList files
    batchContent = os.listdir(os.path.join(nftBatch_save_path, batch1))
    batchContent = [x for x in batchContent if (x not in removeList)]

    if "Images" in batchContent:
        images = True
    if "Animations" in batchContent:
        animations = True
    if "Models" in batchContent:
        models = True
    if "BMNFT_metaData" in batchContent:
        metaData = True

    return images, animations, models, metaData

def getMetaDataDirty(completeMetaDataPath, i):
    """
    Retrieves a given batches data determined by renderBatch in config.py
    """

    file_name = os.path.join(completeMetaDataPath, i)
    metaDataDirty = json.load(open(file_name))

    name = metaDataDirty["name"]
    NFT_DNA = metaDataDirty["NFT_DNA"]
    NFT_Variants = metaDataDirty["NFT_Variants"]

    for i in NFT_Variants:
        x = NFT_Variants[i]
        NFT_Variants[i] = x.split("_")[0]

    return name, NFT_DNA, NFT_Variants

def sendMetaDataToJson(metaDataDict, metaDataPath, jsonName):
    jsonMetaData = json.dumps(metaDataDict, indent=1, ensure_ascii=True)
    with open(os.path.join(metaDataPath, jsonName), 'w') as outfile:
        outfile.write(jsonMetaData + '\n')

def renameMetaData(rename_MetaData_Variables):
    metaDataListOld = os.listdir(rename_MetaData_Variables.completeMetaDataPath)
    cardanoMetaDataPath = os.path.join(rename_MetaData_Variables.completeCollPath, "Cardano_metaData")
    solanaMetaDataPath = os.path.join(rename_MetaData_Variables.completeCollPath, "Solana_metaData")
    erc721MetaDataPath = os.path.join(rename_MetaData_Variables.completeCollPath, "Erc721_metaData")
    openSeaMetaDataPath = os.path.join(rename_MetaData_Variables.completeCollPath, "OpenSea_metaData")

    for i in metaDataListOld:
        name, NFT_DNA, NFT_Variants = getMetaDataDirty(rename_MetaData_Variables.completeMetaDataPath, i)

        file_name = os.path.splitext(i)[0]
        file_num = file_name.split("_")[1]

        if rename_MetaData_Variables.cardanoMetaDataBool:
            if not os.path.exists(cardanoMetaDataPath):
                os.mkdir(cardanoMetaDataPath)

            cardanoJsonNew = "Cardano_" + i
            cardanoNewName = name.split("_")[0] + "_" + str(file_num)

            metaDataDictCardano = Metadata.returnCardanoMetaData(cardanoNewName, NFT_DNA, NFT_Variants, rename_MetaData_Variables.custom_Fields_File, rename_MetaData_Variables.enableCustomFields, rename_MetaData_Variables.cardano_description)

            sendMetaDataToJson(metaDataDictCardano, cardanoMetaDataPath, cardanoJsonNew,)

        if rename_MetaData_Variables.solanaMetaDataBool:
            if not os.path.exists(solanaMetaDataPath):
                os.mkdir(solanaMetaDataPath)

            solanaJsonNew = "Solana_" + i
            solanaNewName = name.split("_")[0] + "_" + str(file_num)

            metaDataDictSolana = Metadata.returnSolanaMetaData(solanaNewName, NFT_DNA, NFT_Variants, rename_MetaData_Variables.custom_Fields_File, rename_MetaData_Variables.enableCustomFields, rename_MetaData_Variables.solana_description)

            sendMetaDataToJson(metaDataDictSolana, solanaMetaDataPath, solanaJsonNew)

        if rename_MetaData_Variables.erc721MetaData:
            if not os.path.exists(erc721MetaDataPath):
                os.mkdir(erc721MetaDataPath)

            erc721JsonNew = "Erc721_" + i
            erc721NewName = name.split("_")[0] + "_" + str(file_num)

            metaDataDictErc721 = Metadata.returnErc721MetaData(erc721NewName, NFT_DNA, NFT_Variants, rename_MetaData_Variables.custom_Fields_File, rename_MetaData_Variables.enableCustomFields, rename_MetaData_Variables.erc721_description)

            sendMetaDataToJson(metaDataDictErc721, erc721MetaDataPath, erc721JsonNew)

        if rename_MetaData_Variables.openSeaMetaData:
            if not os.path.exists(openSeaMetaDataPath):
                os.mkdir(openSeaMetaDataPath)

            openSeaNewName = name.split("_")[0] + "_" + str(file_num)+".json"
            if len(rename_MetaData_Variables.openSea_description) < 1:
                rename_MetaData_Variables.openSea_description = openSeaNewName

            metaDataDictOpenSea = Metadata.returnOpenSeaMetaData(openSeaNewName, NFT_DNA, NFT_Variants, rename_MetaData_Variables.custom_Fields_File, rename_MetaData_Variables.enableCustomFields, rename_MetaData_Variables.openSea_description)

            sendMetaDataToJson(metaDataDictOpenSea, openSeaMetaDataPath, openSeaNewName)
    return

def nftPortFileUploader(apikey, file):
    response = requests.post(
        "https://api.nftport.xyz/v0/files",
        headers={"Authorization": apikey},
        files={"file": file}
    )
    
    return json.loads(response.text)

def nftPortMetaUploader(apikey, metaData):
    response = requests.post(
        "https://api.nftport.xyz/v0/metadata",
        headers={"Authorization": apikey, "Content-Type": "appication/json"},
        data=json.dumps(metaData, indent=4) 
    )
    
    return json.loads(response.text)

def minter(apikey, meta, CONTRACT_ADDRESS, MINT_TO_ADDRESS):
    mintInfo = {
        'chain': 'polygon',
        'contract_address': CONTRACT_ADDRESS,
        'metadata_uri': meta['metadata_uri'],
        'mint_to_address': MINT_TO_ADDRESS,
        'token_id': meta['custom_fields']['edition']
    }
    response = requests.post(
        "https://api.nftport.xyz/v0/mints/customizable",
        headers={"Authorization": apikey, "Content-Type": "appication/json"},
        data=json.dumps(mintInfo, indent=4) 
    )

    return json.loads(response.text)

def uploadToNFTPort(nftport_panel_input):
    file = f"{nftport_panel_input.modelPath}\{nftport_panel_input.fileName}.glb"
    with open(file, 'rb') as modelFile:
        res = nftPortFileUploader(nftport_panel_input.apikey, modelFile)
        resModelUrl = f"{res['ipfs_url']}?fileName={nftport_panel_input.fileName}.glb"

    file = f"{nftport_panel_input.imagePath}\{nftport_panel_input.fileName}.png"
    with open(file, 'rb') as imageFile:
        res = nftPortFileUploader(nftport_panel_input.apikey, imageFile)
        resImageUrl = f"{res['ipfs_url']}"

    file = f"{nftport_panel_input.metaDataPath}\{nftport_panel_input.fileName}.json"
    with open(file, 'r') as inputFile:
        metaData = json.load(inputFile)
        metaData['animation_url'] = resModelUrl
        metaData['file_url'] = resImageUrl
        metaData['custom_fields'] = {
            'edition': round(time.time() * 1000)
        }
    res = nftPortMetaUploader(nftport_panel_input.apikey, metaData)
    metaData['metadata_uri'] = res['metadata_uri']
    with open(file, 'w') as outputFile:
        json.dump(metaData, outputFile, ensure_ascii=False, indent=4)

    # print(f"resUrl {resModelUrl}")
    # print(f"resImageUrl {resImageUrl}")
    # print(f"metaData {metaData}")
    
    return metaData
        
def uploadNFTCollection(uploader_panel_input):
    # print(f"nftport api key {uploader_panel_input.nftport_api_key}")
    # print(f"contract address {uploader_panel_input.contract_address}")
    # print(f"wallet address {uploader_panel_input.wallet_address}")

    completeCollPath = os.path.join(uploader_panel_input.save_path, "Aiz_Blender_NFT_Output", "Complete_Collection")
    completeImagePath = os.path.join(completeCollPath, "Images")
    completeAnimationsPath = os.path.join(completeCollPath, "Animations")
    completeModelsPath = os.path.join(completeCollPath, "Models")
    openSeaMetaDataPath = os.path.join(completeCollPath, "OpenSea_metaData")

    # print(f"completeCollPath {completeCollPath}")
    # print(f"completeImagePath {completeImagePath}")
    # print(f"completeAnimationsPath {completeAnimationsPath}")
    # print(f"completeModelsPath {completeModelsPath}")

    class nftport_panel_input:
        apikey = uploader_panel_input.nftport_api_key
        modelPath = completeModelsPath
        imagePath = completeImagePath
        metaDataPath = openSeaMetaDataPath
        fileName = ""

    onlyfiles = [f for f in listdir(completeModelsPath) if isfile(join(completeModelsPath, f))]

    print(onlyfiles)
    allMetadata = []
    for file in onlyfiles:
        fileName = file.split(".")[0]
        nftport_panel_input.fileName = fileName
        metaData = uploadToNFTPort(nftport_panel_input)
        allMetadata.append(metaData)
    # file = f"{nftport_panel_input.metaDataPath}\_ipfsMetas.json"
    # with open(file, 'w') as outputFile:
    #     json.dump(allMetadata, outputFile, ensure_ascii=False, indent=4)
    print(allMetadata)
    for meta in allMetadata:
        minted = minter(nftport_panel_input.apikey, meta, uploader_panel_input.contract_address, uploader_panel_input.wallet_address)
        print(minted)
        file = f"{nftport_panel_input.metaDataPath}\{meta['custom_fields']['edition']}_minted.json"
        with open(file, 'w') as outputFile:
            json.dump(minted, outputFile, ensure_ascii=False, indent=4)
    print("All Minted")
    
    
if __name__ == '__main__':
    uploadNFTCollection()
