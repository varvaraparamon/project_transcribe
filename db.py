from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from config import DB_URL

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Transcript(Base):
    __tablename__ = 'transcripts'
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    transcription = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine, checkfirst=True)

def insert_transcript(filename, transcription):
    session = Session()
    transcript = Transcript(filename=filename, transcription=transcription)
    session.add(transcript)
    session.commit()
    session.close()

def get_all_transcripts():
    session = Session()
    transcripts = session.query(Transcript.filename, Transcript.created_at, Transcript.id).order_by(Transcript.created_at.desc()).all()
    session.close()
    return transcripts

def get_transcript_by_id(transcript_id):
    session = Session()
    transcript = session.query(Transcript).filter_by(id=transcript_id).first()
    session.close()
    return transcript

