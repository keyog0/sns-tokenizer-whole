from pydantic import BaseModel
from typing import Optional, List, Union, Any

class RequestModel(BaseModel):
    text: str

class RequestModelKiwi(RequestModel):
    text: Union[str,List[str]]

class ResponseModelKiwiSpace(RequestModel):
    text: Any#Union[str,List[str]]

class GraphFrameModel(BaseModel) :
    src: List[str]
    dst: List[List[str]]
    
class KiwiGraphFrameModel(BaseModel) :
    src: List[str]
    dst: List[List[str]]
    
class NoriModel(BaseModel) :
    tokens: List[str]
    
class NoriWithTagModel(BaseModel) :
    token: str
    posType: str
    tag: str

class OktWithTagModel(BaseModel) :
    token: str
    tag: str
    
class KiwiWithTagModel(BaseModel) :
    token: str
    tag: str
    pureTag: str
    start: int
    length: int
    
class OktModel(BaseModel) :
    hashtag: List[str]
    tokens: List[str]
    
class KiwiModel(BaseModel):
    noun: List[str]
    adjective: List[str]
    wordCount: List[int]
    nnpCount: List[int]

class ResponseTokenize(BaseModel):
    graphframe: GraphFrameModel
    nori: NoriModel
    okt: OktModel
    
class ResponseNoriWithTagModel(BaseModel):
    nori: List[NoriWithTagModel]

class ResponseOktWithTagModel(BaseModel):
    okt: List[OktWithTagModel]
    
class ResponseKiwiWithTagModel(BaseModel):
    kiwi: List[KiwiWithTagModel]
    
class ResponseKiwiExtractPhrases(BaseModel):
    kiwi_phrases: List[str]

class ResponseSentence(BaseModel):
    sentence: List[str]
    
class SentenceTokenModel(BaseModel) :
    nori_tokens: List[str]
    okt_tokens: List[str]

class ResponseSentenceTokenize(BaseModel):
    sentence_token: List[SentenceTokenModel]
    
class ResponseClickhouseTokenize(BaseModel):
    okt: OktModel
    kiwi: KiwiModel
    graphframe: GraphFrameModel
    kiwiGraphframe: KiwiGraphFrameModel
    
class ResponseClickhouseTokenizeKiwi(BaseModel):
    kiwi: KiwiModel
    kiwiGraphframe: KiwiGraphFrameModel
    
class ResponseClickhouseTokenizeOkt(BaseModel):
    okt: OktModel
    graphframe: GraphFrameModel