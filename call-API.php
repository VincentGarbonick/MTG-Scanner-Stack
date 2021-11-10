<?php
    // success flag. If it works, redirect the user. If it fails, print out error to them. 
    $success = false; 
    $message = "test";


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
        
        if(file_put_contents("art-and-names.json", file_get_contents($url))) 
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