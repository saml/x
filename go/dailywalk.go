package main

import (
	"fmt"
	"math/rand"
	"sync"
	"time"
)

func sleepRand(min int, max int) time.Duration {
	msec := time.Duration(rand.Intn(max-min) + min)
	time.Sleep(msec * time.Millisecond)
	return msec
}

func act(wg *sync.WaitGroup, name string, action string) {
	defer wg.Done()
	fmt.Printf("%s started %s\n", name, action)
	msec := sleepRand(60, 90)
	fmt.Printf("%s spent %d seconds %s\n", name, msec, action)
}

func startAlarm(c chan string) {
	fmt.Println("Alarm is counting down.")
	sleepRand(10, 100)
	c <- "alarm"
}

func dailyWalk(names ...string) {
	n := len(names)

	// get ready
	var wg sync.WaitGroup
	wg.Add(n)
	for _, name := range names {
		go act(&wg, name, "getting ready")
	}
	wg.Wait()

	// start alarm and put on shoes
	c := make(chan string)
	go startAlarm(c)

	wg.Add(n)
	for _, name := range names {
		go act(&wg, name, "putting on shoes")
	}

	<-c
	fmt.Println("Alarm is armed.")
	wg.Wait() // how can I do  <-c and wg.Wait() in parallel and whoever finishes first wins? If alarm rings first, game over.
	fmt.Println("Exiting and locking the door.")
}

func main() {
	fmt.Println("Let's go for a walk!")
	dailyWalk("Alice", "Bob")
}
