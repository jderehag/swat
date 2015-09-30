#!/usr/bin/env python
'''
Copyright (c) 2015, Jesper Derehag <jesper.derehag@ericsson.com> for Ericsson AB
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions
and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

**************************    THIS LINE IS 120 CHARACTERS WIDE - DO *NOT* EXCEED 120 CHARACTERS!    *******************
'''
from sqlalchemy.ext.declarative import declarative_base as real_declarative_base

from sqlalchemy import Column, Integer, String, VARBINARY, DateTime, ForeignKey, UniqueConstraint, Float
from sqlalchemy import types
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property



from datetime import datetime
import time
from collections import OrderedDict
from sqlalchemy.dialects.mysql.base import DECIMAL

'''
#######################################################################################################################
# Specialized types
#######################################################################################################################
'''
class OptimizedDateTime(DateTime):
    '''
    The OptimizedDateTime is a DBAPI level wrapper around specifically sqlite since
    by default sqlite stores DateTime as strings which is really inefficient.
    '''
    def __init__(self, *kwargs):
        super(OptimizedDateTime, self).__init__(*kwargs)

    def result_processor(self, dialect, coltype):
        if dialect.name == 'sqlite':
            def process(value):  # pylint: disable=C0111
                if value is not None:
                    value = datetime.fromtimestamp(int(value))
                return value
            return process
        else:
            return super(OptimizedDateTime, self).result_processor(dialect, coltype)

    def bind_processor(self, dialect):
        if dialect.name == 'sqlite':
            def process(value):  # pylint: disable=C0111
                if value is not None:
                    value = int(time.mktime(value.timetuple()))
                return value
            return process
        else:
            return super(OptimizedDateTime, self).bind_processor(dialect)

    def adapt(self, *kwargs):
        return OptimizedDateTime(*kwargs)


class HighPrecisionFloat(types.TypeDecorator):
    '''
    HighPrecisionFloat is used to circumvent the very sparse float implementation in mysql.
    floats are only stored using 4 bytes resulting in too low precision for some calculations.
    '''
    # pylint: disable=W0223
    impl = Float
    def __init__(self, *kwargs):
        super(HighPrecisionFloat, self).__init__(*kwargs)

    def load_dialect_impl(self, dialect):
        if dialect.name == 'mysql':
            return dialect.type_descriptor(DECIMAL(precision=20, scale=10))
        else:
            return dialect.type_descriptor(Float)


declarative_base = lambda cls: real_declarative_base(cls=cls)

@declarative_base
class Base(object):
    '''
    Base extends declarative_base with general-purpose methods like __repr__, and _asdict.
    Particularly _asdict is powerful in terms of beeing able to directly serialize an object into json.
    '''
    @property
    def columns(self):
        '''
        Contains a list of all column names
        '''
        return [c.name for c in self.__table__.columns]

    @property
    def columnitems(self):
        '''
        Contains a dictionary with all column items, with column name as key
        '''
        return {c.name: c for c in self.__table__.columns}

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.columnitems)

    def _asdict(self):
        result = OrderedDict()
        for column in self.columns:
            result[column] = getattr(self, column)
        return result

    def tojson(self):
        '''
        Returns a OrderedDict of all columns, a bit awkward notation.
        This function will likely be removed in the future.
        '''
        return self._asdict()

'''
#######################################################################################################################
# ORM models
#######################################################################################################################
'''


class Subsystem(Base):
    '''
    subsystem, a container for a group of files and typically belongs to a maintainer
    '''
    __tablename__ = 'subsystem'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    subsystem = Column(VARBINARY(255), unique=True)
    status = Column(String(255))
    maintainer = Column(String(255))

    files = relationship("File", backref=backref('subsystem'))


class File(Base):
    '''
    A table representing a file
    '''
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    subsystem_id = Column(Integer, ForeignKey('subsystem.id'), nullable=True)
    file = Column(VARBINARY(255), unique=True)

    functions = relationship("Function", backref=backref('file'), cascade_backrefs=True,
                             cascade='all, delete-orphan', single_parent=True)
    defect_mods = relationship("DefectModification", backref=backref('file'), cascade_backrefs=True,
                               cascade='all, delete-orphan', single_parent=True)
    change_metrics = relationship("ChangeMetric", backref=backref('file'), cascade_backrefs=True,
                                  cascade='all, delete-orphan', single_parent=True)


class Function(Base):
    '''
    A table representing a function, which typically belongs to a file
    '''
    __tablename__ = 'function'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    file_id = Column(Integer, ForeignKey('file.id'), nullable=False)
    function = Column(VARBINARY(255))
    __table_args__ = (UniqueConstraint('file_id', 'function'),)

    defect_mods = relationship("DefectModification", backref=backref('function'), cascade_backrefs=True,
                               cascade='all, delete-orphan', single_parent=True)

    change_metrics = relationship("ChangeMetric", backref=backref('function'), cascade_backrefs=True,
                                  cascade='all, delete-orphan', single_parent=True)


class Version(Base):
    '''
    A table representing a versions of a file, for instance a commit hash in git
    '''
    __tablename__ = 'version'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    version = Column(VARBINARY(255), unique=True)

    defect_mods = relationship("DefectModification", backref=backref('version'), cascade_backrefs=True,
                               cascade='all, delete-orphan', single_parent=True)
    change_metrics = relationship("ChangeMetric", backref=backref('version'), cascade_backrefs=True,
                                  cascade='all, delete-orphan', single_parent=True)


class User(Base):
    '''
    A table representing users (contributors) to files
    '''
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user = Column(VARBINARY(255), unique=True)

    defect_mods = relationship("DefectModification", backref=backref('user'))
    change_metrics = relationship("ChangeMetric", backref=backref('user'))


class DefectModification(Base):
    '''
    A table representing defect modifications
    Meaning, a commit that has been marked as a defect (with a valid defect_id).
    '''
    __tablename__ = 'defect_modifications'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    file_id = Column(Integer, ForeignKey('file.id'), nullable=False)
    version_id = Column(Integer, ForeignKey('version.id'), nullable=False)
    function_id = Column(Integer, ForeignKey('function.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    defect_id = Column(Integer)
    date = Column(OptimizedDateTime)
    __table_args__ = (UniqueConstraint('file_id', 'version_id', 'function_id'),)


class DefectMeta(Base):
    '''
    A table representing defects as reported into a change management system.
    In other words, this represents metadata in a bug reporting system.
    '''
    __tablename__ = 'defects_meta'
    id = Column(Integer, primary_key=True, unique=True)
    submitted_on = Column(OptimizedDateTime)
    severity = Column(String(50))
    product = Column(String(50))
    answer_code = Column(String(50))
    fault_code = Column(String(50))


class ChangeMetric(Base):
    '''
    A table representing a change due to a new version
    '''
    __tablename__ = 'change_metrics'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    file_id = Column(Integer, ForeignKey('file.id'), nullable=False)
    version_id = Column(Integer, ForeignKey('version.id'), nullable=False)
    function_id = Column(Integer, ForeignKey('function.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    date = Column(OptimizedDateTime)
    added = Column(Integer, nullable=True)
    changed = Column(Integer, nullable=True)
    deleted = Column(Integer, nullable=True)
    nloc = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=True)
    parameter_count = Column(Integer, nullable=True)
    cyclomatic_complexity = Column(Integer, nullable=True)

    __table_args__ = (UniqueConstraint('file_id', 'version_id', 'function_id'),)


class Eav(Base):
    '''
    Used as a generic key-value store.
    I.e Entity-attribute-value:
    http://en.wikipedia.org/wiki/Entity%E2%80%93attribute%E2%80%93value_model

    Very low-performance and typically storing things like when the database was last updated.
    '''
    __tablename__ = 'eav_store'
    key = Column(VARBINARY(255), primary_key=True, unique=True)
    value_ = Column(String(255))
    type = Column(String(255))

    @hybrid_property
    def value(self):
        '''
        Getter for eav value, it tries to figure out type of value from db, and then cast it into the corresponding
        python type before returning.

        Could maybe be changed to dynamic typing using type() function
        type = type(value).__name__ and something corresponding for setter
        '''
        value = self.value_
        try:
            if self.type == 'datetime':
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            elif self.type == 'int':
                value = int(value)
        except:
            pass

        return value

    @value.setter
    def value(self, value):
        '''
        Setter for eav value, it tries to figure out type of value, and then transform it into a str representation
        for the db.
        '''
        type_ = 'str'
        if isinstance(value, datetime):
            type_ = 'datetime'
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, int):
            type_ = 'int'
            value = int(value)

        self.value_ = str(value)
        self.type = type_

