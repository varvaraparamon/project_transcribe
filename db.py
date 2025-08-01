from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, joinedload
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
    
    venue_id = Column(Integer, ForeignKey('venues.id'))
    venue = relationship("Venue")

class Venue(Base):
    __tablename__ = 'venues'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    transcripts = relationship('Transcript', back_populates='venue')

def init_db():
    Base.metadata.create_all(engine, checkfirst=True)

def insert_transcript(filename, transcription, venue_id):
    session = Session()
    transcript = Transcript(filename=filename, transcription=transcription, venue_id=venue_id)
    session.add(transcript)
    session.commit()
    transcript_id = transcript.id
    session.close()
    return transcript_id
    

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

def get_all_venues():
    session = Session()
    venues = session.query(Venue).all()
    session.close()
    return venues


def get_venue_by_transcript_id(transcript_id):
    session = Session()
    transcript = session.query(Transcript)\
        .options(joinedload(Transcript.venue))\
        .filter_by(id=transcript_id)\
        .first()
    session.close()
    if transcript:
        return transcript.venue
    return None

