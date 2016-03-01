package main

import (
	"fmt"
	"math/rand"
	"time"
)

type eventstype struct {
	gettingReady   string
	puttingOnShoes string
	alarm          string
}

// for auto complete. meh
var events = eventstype{
	gettingReady:   "getting ready",
	puttingOnShoes: "putting on shoes",
	alarm:          "alarm",
}

func sleepRand(min int, max int) time.Duration {
	msec := time.Duration(rand.Intn(max-min+1) + min)
	time.Sleep(msec * time.Millisecond)
	return msec
}

// given name performs given action for duration of [min,max].
// and it shouts with mouth.
func act(mouth chan string, name string, action string, min int, max int) {
	fmt.Printf("%s started %s\n", name, action)
	msec := sleepRand(min, max)
	fmt.Printf("%s spent %d seconds %s\n", name, msec, action)
	mouth <- action // Ma, I did it!
}

func yell(c chan string, n int) {
	for i := 0; i < n; i++ {
		c <- ""
	}
}

func newPerson(mouth chan string, ear chan string, name string) {
	// a person gets ready and shouts he/she is ready
	act(mouth, name, events.gettingReady, 60, 90)

	// listens/waits until other people finish
	<-ear

	// then they put on shoes and shouts
	act(mouth, name, events.puttingOnShoes, 35, 45)
}

func startAlarm(c chan string) {
	fmt.Println("Alarm is counting down.")
	sleepRand(60, 60)
	c <- events.alarm
}

func dailyWalk(names ...string) {
	n := len(names)

	mouth := make(chan string)
	ear := make(chan string)

	for _, name := range names {
		go newPerson(mouth, ear, name)
	}

	ready := 0
	shoes := 0
	for {
		sentence := <-mouth
		if sentence == events.gettingReady {
			ready++
			if ready == n {
				// everybody's ready.
				yell(ear, n) // yell to start putting on shoes
				go startAlarm(mouth)
			}
		} else if sentence == events.puttingOnShoes {
			shoes++
			if shoes == n {
				// everybody wore shoes.
				fmt.Println("Exiting and locking the door.")
			}
		} else if sentence == events.alarm {
			fmt.Println("Alarm is armed")
			break // game over. alarm rang first. did not get to lock the door in time.
		}
	}
}

func main() {
	fmt.Println("Let's go for a walk!")
	dailyWalk("Alice", "Bob")
}
