#!/usr/bin/php
<?php
 /** LICENCE
  This converter is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
  */

error_reporting(0);

if(!empty($argc)){
	$file = $argv[1];
	print "Converting $file ...\n";
	
	if(file_exists($file)){
		$nome = explode('.',$file);
		$nome = $nome[0];
			
		$fp = fopen($file,'r') 
				or die("[Error] Can't open $file file!\n");
				
		$fo = fopen('output.c','w')
				or die("[Error] Can't create output.c file!\n");
		
		//Cabeçalho da imagem
		$header = array();
		for($i=0;$i<=3;$i++){
			$header[$i] = fgets($fp);
		}
		
		if(count($header)==4){ //not a real check but works
			fwrite($fo,'//Generated by  : ppmconvert v0.1' . "\n");
			fwrite($fo,'//File          : ' . $file . "\n");
			
			$header[2] = str_replace(' ','x',$header[2]);
			fwrite($fo,'//Dimensions    : ' .$header[2]. "\n\n");
			
			//Array
			fwrite($fo,"const unsigned int ${nome}[]={\n"); 
			
		}
		else{
			die("[Error] File not a valid Gimp PPM file\n");
		}
		
		//Dados da imagem R G B
		$header[2] = str_replace('x','*',$header[2]);
		eval('$total=' . $header[2] . ' - 1;');
	
		$count = 0;
		
		while (!feof($fp)){
            //linha do arquivo...
            // 565rgb = ((red and 0xF8)<<8) + ((green and 0xFC)<<3) + ((blue and 0xF8)>>3)
            $red 	= fgets($fp);
            $green	= fgets($fp);
            $blue	= fgets($fp);
                        
            $rgb = (($red & 0xF8)<<8) + (($green & 0xFC)<<3) + (($blue & 0xF8)>>3);
            $rgb = dechex($rgb);
            
            if($count != $total)
				fwrite($fo,'0x' . $rgb . ', ');
			else{
				fwrite($fo,'0x' . $rgb);
				break;
			}
            
            $count++;
            if(!($count%16)){
				fwrite($fo,"\n");
			}
		}
		
		fwrite($fo,"\n};\n");
				
		fclose($fp);
		fclose($fo);
	}
}
?>
