#!/usr/bin/php
<?php

var_dump($argv);

$frames = scandir($argv[1]);
chdir($argv[1]);

// remove . and .. references
array_shift($frames);
array_shift($frames);

for ($x = 0; $x < count($frames) - 1; ) {
    for ($y = $x + 1; $y < count($frames); $y++) {
        $diff = shell_exec("compare -metric RMSE $frames[$x] $frames[$y] NULL: 2>&1");

        if ($diff < 5000 && $diff != 0) {
            unlink($frames[$y]);
            //echo "Deleted $frames[$y] \n";
        } else {
            $x = $y;
            break;
        }
    }
}