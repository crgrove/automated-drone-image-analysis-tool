from PIL import Image

class ExifTransfer:
    @staticmethod
    def transfer_exif(originFile, destinationFile):
        """
        transfer_exif copies the exif information of an image file to another image file
        
        :String originFile: the path to the source file
        :String destinationFile: the path to the destination file
        """

        # load old image and extract EXIF
        image = Image.open(originFile)
        exif = image.info['exif']

        # load new image
        image_new = Image.open(destinationFile)
        image_new.save(destinationFile, 'JPEG', exif=exif)