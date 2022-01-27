<?php
    // success flag. If it works, redirect the user. If it fails, print out error to them. 
    $success = false; 
    $message = "test";

    $bulkJsonName = "art-and-names.json";

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
        $file = file_get_contents($jsonFileName);

        while(!$file)
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

            $file = file_get_contents($jsonFileName);
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

        // loop through each record of table 
        for ($row_num = 0; $row_num < $num_rows; $row_num++) {
            $values = array_values($row);
            print $values[0];
            echo "<br>";
            $row = mysqli_fetch_array($result);
        } 
    }
    else 
    {
        echo "uh oh";
    }



?>