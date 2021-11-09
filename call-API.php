<?php
    // success flag. If it works, redirect the user. If it fails, print out error to them. 
    $success = false; 
    $message = "test";


    // Useage: Downloads the bulk JSON file from the gatherer
    // Precondition: None
    // Postcondition: File with json information
    function downloadBulk()
    {

    };



    if(isset($_POST["update-info-button"]))
    {
        $jsonRequest = "https://api.scryfall.com/bulk-data";
        /*
        $ch = curl_init("https://api.scryfall.com/bulk-data"); 
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HEADER, 0);
        $data = curl_exec($ch);
        echo $data;
        print($data);
        curl_close($ch);
        */

        
        $json = file_get_contents($jsonRequest,0,null,null);  
        $json_output = json_encode($json, TRUE); 
        header('Content-Type: application/json');
        echo $json_output;

    }
    elseif(isset($_POST["process-image-button"]))
    {
        echo "process";
    }
    elseif(isset($_POST["price-button"]))
    {
        echo "price";
    }
    else 
    {
        echo "uh oh";
    }
?>