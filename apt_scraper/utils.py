import re
import string

class Utils:

    def has_carriage_return(self, target):
        if "\r\n" in target:
            return True

        return False

    def remove_all_chars(self,target):

        target = target.replace('\r\n','')
        target=''.join(c for c in target if not c.isalpha())

        #'!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'
        target = target.translate(str.maketrans('', '', string.punctuation))
        return target.strip()

    def remove_carriage_display(self,target):
        target = target.replace('\r\n','')
        return target.strip()
