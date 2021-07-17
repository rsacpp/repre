#include "ace/SString.h"
#include "ace/Log_Msg.h"
#include <openssl/evp.h>

int
ACE_TMAIN(int argc, ACE_TCHAR* argv[]){
  ACE_CString* s0 = new ACE_CString(argv[1]);
  ACE_DEBUG((LM_INFO,
	     "%s\n", s0->c_str()));

  EVP_MD_CTX* context = EVP_MD_CTX_new();
  
  if((context!= NULL) &&
     EVP_DigestInit_ex(context, EVP_sha3_256(), NULL) &&
     EVP_DigestUpdate(context, s0->c_str(), s0->length())
     ){
	unsigned char  hash[EVP_MAX_MD_SIZE];
	unsigned int lengthOfHash =0;

	if(EVP_DigestFinal_ex(context, hash, &lengthOfHash)){

	  if(hash[0] == 0x80){
	    for(int i = 0 ; i< lengthOfHash; i++){
	      ACE_DEBUG((LM_INFO,
			 "%x", hash[i]));
	    }
	    ACE_DEBUG((LM_INFO,
		       "\n"));
	  }
	}
  }

  EVP_MD_CTX_free(context);
  delete s0;
  return 0;
}
