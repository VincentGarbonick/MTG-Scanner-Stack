<?php
    // success flag. If it works, redirect the user. If it fails, print out error to them. 
    $success = false; 
    $message = "test";

    $bulkJsonName = "art-and-names.json";
    
    function myCurlInit()
    {
        /*
        $ch = curl_init();
        //curl_setopt($ch, CURLOPT_URL, "http://www.google.com");
        curl_setopt($ch, CURLOPT_URL, "https://api.scryfall.com/cards/search?q=Knight of the White Orchid");
        curl_setopt($ch, CURLOPT_HEADER, 0);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); // For HTTPS
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false); // For HTTPS
        $response=curl_exec($ch);
        echo $response; 
        sleep(1);
        curl_setopt($ch, CURLOPT_URL, "https://api.scryfall.com/cards/search?q=Thragtusk");
        $response = curl_exec($ch);
        //echo $response;
        curl_close($ch);   
        */
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_HEADER, 0);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); // For HTTPS
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false); // For HTTPS

        return $ch;
    }

    function curlSearch($ch, $searchName)
    {
        curl_setopt($ch, CURLOPT_URL, "https://api.scryfall.com/cards/search?q=$searchName");
        $response = curl_exec($ch);
        echo $response;
    }
    // Useage: Downloads the bulk JSON art file from scryfall 
    // Precondition: None
    // Postcondition: File with json information on each card artwork 
    if(isset($_POST["update-info-button"]))
    {
        // bulk list of cards 
        // https://c2.scryfall.com/file/scryfall-bulk/default-cards/default-cards-20211110100240.json

        // unique artwork
        // https://c2.scryfall.com/file/scryfall-bulk/unique-artwork/unique-artwork-20211110101336.json

        // set a high memory limit since this is a huge file 
        ini_set('memory_limit','500M');

        $url = "https://c2.scryfall.com/file/scryfall-bulk/unique-artwork/unique-artwork-20211110101336.json";
        
        if(file_put_contents($bulkJsonName, file_get_contents($url))) 
        {
           header("Location: developer.html"); 
        }
        else
        {
            echo("Bad download response, something is wrong.");
        }
    }
    elseif(isset($_POST["process-image-button"]))
    {   
        // set a high memory limit since this file is huge 
        ini_set('memory_limit','500M');
        
        // to prevent timeout 
        ini_set('max_execution_time', '0');

        // check if directory exists and make one if needed
        if(!file_exists("./img"))
        {
            mkdir("./img", 0777);
        }

        /*
        This is what the json object for all the names and arts looks like 

        [ 
            {json object},
            {json object},
            ...
            {last json object}
        ]

        we are look at this file like a plaintext file, removing the comma at the end,
        then decoding the file as json. we must remove the comma or else an error will be thrown
        */

        $file = fopen($bulkJsonName, "r");

        if($file)
        {   
            while(!feof($file))
            {
                $line = fgets($file);
                // we are getting rid of the comma at the end of each json line so the json is
                // not malformed, which can cause failed decodes
                // the comma is the second to last value in the string for some strange reason
                $line = substr_replace($line,"",-2);
                $line = json_decode($line, TRUE);
                //TODO: GET FINAL CARD WORKING 
                if($line)
                {
                    $imgName = $line["name"];
                    // if there is a // in the name (like some adventure cards), fix
                    if(strpos($imgName, "//"))
                    {
                        $imgName = str_replace("//", "", $imgName);
                    }

                    $url = $line["image_uris"]["small"];
                    //echo $url;
                    //echo "<br>";                        
                    
                    // if we don't have an image URL, that means the card is double faced 
                    if(!$url)
                    {
                        // TODO: GET DOUBLE FACED CARDS WORKING
                        // just set it to fury sliver for now 
                        $url = "https://c1.scryfall.com/file/scryfall-cards/small/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979";

                        // we are going to have to replace the double slashes in the name too 
                        // WE WILL HAVE TO WORRY ABOUT THIS WHEN MATCHING THE CARDNAME 
                        $imgName = str_replace("//", "", $imgName);
                        //echo "./img/" . $imgName . ".jpg";
                        //echo "<br>";
                        //echo "DOUBLE FACED CARD DETECTED";
                        //echo "<br>";
                        //echo $url;
                        //echo "<br>";
                    }
                    file_put_contents("./img/" . $imgName . ".jpg" , file_get_contents($url));
                }
            }
            echo "ALL DONE";
            fclose($file);
        }



    }
    elseif(isset($_POST["price-button"]))
    {
        // get the json information 
        $jsonFileName = "art-and-names.json";
        $jFile = file_get_contents($jsonFileName);

        // if we don't have a $jsonFileName, which is the place where all the card information resides, we make a new one
        while(!$jFile)
        {
            // set a high memory limit since this is a huge file 
            ini_set('memory_limit','500M');

            $url = "https://c2.scryfall.com/file/scryfall-bulk/unique-artwork/unique-artwork-20211110101336.json";
            
            if(file_put_contents($jsonFileName, file_get_contents($url))) 
            {
               echo "Downloaded info for " . $jsonFileName . "<br>"; 
            }
            else
            {
                echo("Bad download response, something is wrong.");
            }

            $jFile = file_get_contents($jsonFileName);
            echo "hi";
        }

        $hostname = "localhost";
        $username = "root";
        $pass = "";
        $dbName = "magic";
        $tableName = "mtgCards";

        $conn = mysqli_connect($hostname, $username, $pass, $dbName);
        $query = "SELECT * FROM $tableName";

        $result = mysqli_query($conn,$query);
        
        $row = mysqli_fetch_array($result);
        
        $num_rows = mysqli_num_rows($result);
        $num_fields = mysqli_num_fields($result);

        $currentName = "Fury Sliver";


        ini_set('memory_limit','500M'); // set a lot of memory, because we will be scanning 
                                        // a lot of data 
        //echo json_encode(file_get_contents("https://api.scryfall.com/cards/search?q=\"$currentName\""));

        ini_set('max_execution_time', '0'); // it will time out otherwise 

        /*
        echo json_encode(file_get_contents("https://api.scryfall.com/cards/search?q=\"Abrupt%20Decay\""));
        sleep(1);
        echo json_encode(file_get_contents("https://api.scryfall.com/cards/search?q=\"Flickerwisp\""));
        sleep(1);
        echo json_encode(file_get_contents("https://api.scryfall.com/cards/search?q=\"Fury%20Sliver\""));
        sleep(1);
        echo json_encode(file_get_contents("https://api.scryfall.com/cards/search?q=\"Liliana%20Vess\""));
        sleep(1);
        echo json_encode(file_get_contents("https://api.scryfall.com/cards/search?q=\"Thragtusk\""));
        sleep(1);
        echo json_encode(file_get_contents("https://api.scryfall.com/cards/search?q=\"Abrupt%20Decay\""));
        */

        $ch = myCurlInit();
        curlSearch($ch, "Fury Sliver");
        
        // loop through each record of table 
        for ($row_num = 0; $row_num < $num_rows; $row_num++) {
            //$values = array_values($row);
            $values = array_values($row);

            // current name that we are "on" right now 
            $currentName = $values[0];
            $searchString = "https://api.scryfall.com/cards/search?q=\"$currentName\"";

            //$currentJson = json_encode(file_get_contents($searchString));
            echo $searchString."<br>";

            // DOESN'T WORK WITH EITHER OF THESE PLUS THE CURRENTJSON FOR SOME REASON
            //usleep(60 * 1000); // sleep for 6ms, per the insturctions from scryfall
            //sleep(1);
            
            //echo $currentJson."<br"."<br>";
            // loop through each entry in base file 

            /*
            $file = fopen($jsonFileName, "r");

            if($file)
            {
                while(!feof($file))
                {
                    $line = fgets($file);
                    // we are getting rid of the comma at the end of each json line so the json is
                    // not malformed, which can cause failed decodes
                    // the comma is the second to last value in the string for some strange reason
                    $line = substr_replace($line,"",-2);
                    $line = json_decode($line, TRUE);

                    if($line && $line["name"] == $currentName)
                    {
                        //echo "<br>".$line["name"]."==".$currentName."<br>";
                        //echo "<br>"."<br>"."<br>".$line["oracle_text"];
                        // TODO: INCREMENT PROGRESS BAR HERE 
                        break;
                    }
                }
                fclose($file);
            }
            // TODO: ADD PROGRESS BAR 
            */
            $row = mysqli_fetch_array($result);

        } 
        
    }
    else 
    {
        echo "uh oh";
    }



?>