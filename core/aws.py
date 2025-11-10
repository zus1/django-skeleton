import datetime
import logging
import os
import random
import tempfile
import mimetypes

import boto3
from boto3.s3.transfer import S3Transfer
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.uploadedfile import TemporaryUploadedFile
from s3transfer import S3UploadFailedError

from users.constant import UserConstrains
from django.core.files import File


class ClientFactory:
    __instance: BaseClient | None = None

    @classmethod
    def instance(cls):
        if not cls.__instance:
            cls.__instance = boto3.client(
                service_name='s3',
                aws_access_key_id=settings.AWS_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )

        return cls.__instance

class TransferFactory:
    __instance: S3Transfer | None = None
    @classmethod
    def instance(cls, client: BaseClient):
        if not cls.__instance:
            cls.__instance = S3Transfer(client)

        return cls.__instance

class S3Storage(Storage):
    possible_mime_types = [

    ].append(UserConstrains.avatar_supported_types)

    def __init__(self):
        self.__bucket = settings.AWS_S3_BUCKET
        self.__client: BaseClient = ClientFactory.instance()
        self.__s3_transfer: S3Transfer = TransferFactory().instance(self.__client)

    def save(self, name, content: TemporaryUploadedFile, max_length=None):
        new_name = self.__create_filename(name=name, temp_path=content.temporary_file_path())

        try:
            self.__s3_transfer.upload_file(
                bucket=self.__bucket,
                key=new_name,
                filename=content.temporary_file_path()
            )
        except S3UploadFailedError:
            return ''

        return new_name

    def __create_filename(self, name: str, temp_path: str) -> str:
        prefix = self.__create_prefix(name=name)
        extension = self.__guess_extension(temp_path=temp_path)
        new_name = prefix + '/' + (str(random.randrange(10000, 99999)) + '_'
                                   + str(int(datetime.datetime.now().timestamp()))) + extension

        return self.generate_filename(new_name)

    def __create_prefix(self, name: str)->str:
        name_parts = name.split('/')
        if len(name_parts) == 1:
            return ''

        return name_parts[0]

    def __guess_extension(self, temp_path: str)->str:
        mime_type = mimetypes.guess_type(url=temp_path)[0]

        return mimetypes.guess_extension(type=mime_type)

    def open(self, name, mode='rb')->File:
        destination_path = os.path.join(
            tempfile.gettempdir(),
            str(random.randrange(10000, 99999)) +
            '_' + str(int(datetime.datetime.now().timestamp()))
        )

        self.__s3_transfer.download_file(
            bucket=self.__bucket,
            key=name,
            filename=destination_path,
        )

        return File(file=open(destination_path, mode=mode), name=name)

    def delete(self, name: str)->bool:
        response = self.__client.delete_object(
            Bucket=self.__bucket,
            Key=name,
        )

        return response.get('DeleteMarker')

    """
    path == prefix
    """
    def listdir(self, path: str)->list:
        paginator = self.__client.get_paginator('list_objects_v2')

        keys = []
        for page in paginator.paginate(Bucket=self.__bucket, prefix=path):
            for content in page.get('Contents', ()):
                keys.append(content['Key'])

        return keys

    def exists(self, name: str)->bool:
        try:
            self.__client.head_object(
                Bucket=self.__bucket,
                Key=name,
            )
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logging.getLogger('system').error(e.response['Error']['Message'])
                return False

        return True

    '''
    Return presigned url    
    '''
    def url(self, name: str)->str:
        return self.__client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self.__bucket,
                'Key': name,
            },
            ExpiresIn=settings.AWS_S3_SIGNATURE_TTL,
        )