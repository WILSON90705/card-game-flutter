import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/material.dart';
import 'juego.dart';

void main() {
  runApp(MaterialApp(home: CasinoApp()));
}

class CasinoApp extends StatefulWidget {
  const CasinoApp({super.key});
  @override
  // ignore: library_private_types_in_public_api
  _CasinoAppState createState() => _CasinoAppState();
}

class _CasinoAppState extends State<CasinoApp> {
  final TextEditingController userController = TextEditingController();
  final TextEditingController passController = TextEditingController();
  String result = "";
  final Color cardColor = const Color.fromARGB(255, 255, 255, 255);
  bool cambio = false;

  Future<void> loginExitoso(BuildContext context) async {
    print('INTENTO LOGIN');

    try {
      final url = Uri.parse('http://127.0.0.1:8080/casino/login');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'usuario': userController.text,
          'password': passController.text,
        }),
      );

      print('STATUS: ${response.statusCode}');
      print('BODY: ${response.body}');

      if (!mounted) return;

      if (response.statusCode == 200) {
        setState(() {
          cambio = true;
        });
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Login exitoso')));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('contraseña o usuario incorrecto')),
        );
      }
    } catch (e) {
      print('ERROR HTTP: $e');
    }
  }

  Future<void> registrarExitoso(BuildContext context) async {
    try {
      final url2 = Uri.parse('http://127.0.0.1:8080/casino/register');
      final response = await http.post(
        url2,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'usuario': userController.text,
          'password': passController.text,
        }),
      );

      print('STATUS: ${response.statusCode}');
      print('BODY: ${response.body}');

      if (!mounted) return;

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Registro exitoso')));
      } else {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Error en el registro')));
      }
    } catch (e) {
      print('ERROR HTTP: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // IMAGEN DE FONDO
          Positioned.fill(
            child: IgnorePointer(
              child: AnimatedSwitcher(
                duration: const Duration(seconds: 1),
                child: Image.asset(
                  cambio
                      ? 'assets/image/cartas_juego.jpg'
                      : 'assets/image/visual2.png',
                  key: ValueKey(cambio),
                  fit: BoxFit.contain,
                ),
              ),
            ),
          ),
          // CONTENIDO ENCIMA
          Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const SizedBox(height: 20),
                SizedBox(
                  width: 250,
                  child: TextField(
                    controller: userController,
                    decoration: InputDecoration(
                      hintText: 'Usuario',
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 15),
                SizedBox(
                  width: 250,
                  child: TextField(
                    controller: passController,
                    obscureText: true,
                    decoration: InputDecoration(
                      hintText: 'Contraseña',
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                ElevatedButton(
                  onPressed: () async {
                    await loginExitoso(context);
                    //await Navigator.push(
                    //  context,
                    //  MaterialPageRoute(builder: (_) => const Juego()),
                    //);
                    //runApp(
                    //  MaterialApp(
                    ///    home: const Juego(),
                    ///    debugShowCheckedModeBanner: false,
                    //  ),
                    //);

                    runApp(
                      MaterialApp(
                        home: const Juego(),
                        debugShowCheckedModeBanner: false,
                      ),
                    );
                  },

                  child: Text('Login'),
                ),
                const SizedBox(height: 10),
                ElevatedButton(
                  onPressed: () async {
                    await registrarExitoso(context);
                  },
                  child: Text('Registrar'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
