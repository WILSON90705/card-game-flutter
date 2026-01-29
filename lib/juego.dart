import 'package:flutter/material.dart';

List<String> baraja = [
  'assets/image/Back Blue.png',
  'assets/image/1c.png',
  'assets/image/1d.png',
  'assets/image/1h.png',
  'assets/image/1s.png',
  'assets/image/2c.png',
  'assets/image/2d.png',
  'assets/image/2h.png',
  'assets/image/2s.png',
  'assets/image/3c.png',
  'assets/image/3d.png',
  'assets/image/3h.png',
  'assets/image/3s.png',
  'assets/image/4c.png',
  'assets/image/4d.png',
  'assets/image/4h.png',
  'assets/image/4s.png',
  'assets/image/5c.png',
  'assets/image/5d.png',
  'assets/image/5h.png',
  'assets/image/5s.png',
  'assets/image/6c.png',
  'assets/image/6d.png',
  'assets/image/6h.png',
  'assets/image/6s.png',
  'assets/image/7c.png',
  'assets/image/7d.png',
  'assets/image/7h.png',
  'assets/image/7s.png',
  'assets/image/8c.png',
  'assets/image/8d.png',
  'assets/image/8h.png',
  'assets/image/8s.png',
  'assets/image/9c.png',
  'assets/image/9d.png',
  'assets/image/9h.png',
  'assets/image/9s.png',
  'assets/image/10c.png',
  'assets/image/10d.png',
  'assets/image/10h.png',
  'assets/image/10s.png',
  'assets/image/11c.png',
  'assets/image/11d.png',
  'assets/image/11h.png',
  'assets/image/11s.png',
  'assets/image/12c.png',
  'assets/image/12d.png',
  'assets/image/12h.png',
  'assets/image/12s.png',
  'assets/image/13c.png',
  'assets/image/13d.png',
  'assets/image/13h.png',
  'assets/image/13s.png',
  'assets/image/Back Red.png',
];

int continuar = 0;

List<String> baraja2 = [];
List<List<String>> jugador1 = [];
List<List<String>> jugador2 = [];

class Juego extends StatefulWidget {
  const Juego({super.key});

  @override
  State<Juego> createState() => _JuegoState();
}

class _JuegoState extends State<Juego> {
  @override
  void initState() {
    super.initState();
    jugador1.add([]);
    jugador2.add([]);
    baraja2 = List.from(baraja);
    baraja2.shuffle();
    for (int i = 0; i < 5; i++) {
      jugador1[i].add(baraja2.removeAt(0));
      jugador2[i].add(baraja2.removeAt(0));
    }
  }

  Future<int> Numerodejugadores(BuildContext context, int continuar) async {
    if (continuar == 1) {
    } else if (continuar == 2) {}
    return 0;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: 1000,
        height: 1000,
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/image/meza_poker.jpg'),
            fit: BoxFit.cover,
          ),
        ),
        child: Stack(
          alignment: Alignment.center, // centro de la mesa
          children: [
            // MAZO CENTRADO
            SizedBox(
              width: 250,
              height: 250,
              child: Stack(
                children: [
                  for (int i = 0; i < baraja2.length; i++)
                    Positioned(
                      top: i * 0.5,
                      left: i * 0.5,
                      child: Image.asset(baraja2[i], width: 150),
                    ),
                ],
              ),
            ),
            Scaffold(
              appBar: AppBar(title: const Text('Poker')),
              drawer: Drawer(
                child: ListView(
                  children: [
                    DrawerHeader(
                      decoration: BoxDecoration(),
                      child: const Text('Menu'),
                    ),
                    ListTile(
                      title: Text('Jugador 1 '),
                      onTap: () {
                        continuar = 1;
                        Numerodejugadores(context, continuar);
                      },
                    ),
                    ListTile(
                      title: Text('Jugador 2 '),
                      onTap: () {
                        continuar = 2;
                        Numerodejugadores(context, continuar);
                      },
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
