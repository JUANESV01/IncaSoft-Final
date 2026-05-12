from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from datetime import date

from gestion.models import Colaborador, HistorialEstado, Incapacidad, TipoIncapacidad


class Command(BaseCommand):
    help = "Crea usuarios, roles y datos demo para INCASOFT Solutions."

    def handle(self, *args, **options):
        roles = ["Administrador", "Gestion Humana", "Financiera", "Coordinacion", "Gerente"]
        grupos = {nombre: Group.objects.get_or_create(name=nombre)[0] for nombre in roles}

        User = get_user_model()
        admin, _ = User.objects.get_or_create(username="administrador", defaults={"is_staff": True, "is_superuser": True})
        admin.set_password("IncaSoft2026*")
        admin.is_staff = True
        admin.is_superuser = True
        admin.email = "admin@incasoft.local"
        admin.first_name = "Administrador"
        admin.last_name = "INCASOFT"
        admin.save()
        admin.groups.set([grupos["Administrador"]])

        gh, _ = User.objects.get_or_create(username="gestionhumana")
        gh.set_password("IncaSoft2026*")
        gh.first_name = "Laura"
        gh.last_name = "Gestion Humana"
        gh.email = "gestionhumana@incasoft.local"
        gh.is_active = True
        gh.save()
        gh.groups.set([grupos["Gestion Humana"]])

        gerente, _ = User.objects.get_or_create(username="gerente")
        gerente.set_password("IncaSoft2026*")
        gerente.first_name = "Carlos"
        gerente.last_name = "Gerente"
        gerente.email = "gerente@incasoft.local"
        gerente.is_active = True
        gerente.save()
        gerente.groups.set([grupos["Gerente"]])

        tipos = [
            ("Enfermedad general", "EG", "EPS", 180),
            ("Accidente laboral", "AL", "ARL", 540),
            ("Licencia de maternidad", "LM", "EPS", 126),
            ("Licencia de paternidad", "LP", "EPS", 14),
            ("Licencia no remunerada", "LNR", "EMPRESA", 30),
        ]
        tipo_objs = {}
        for nombre, codigo, entidad, dias in tipos:
            tipo, _ = TipoIncapacidad.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre,
                    "entidad_responsable": entidad,
                    "dias_maximos": dias,
                    "requiere_soporte": entidad != "EMPRESA",
                    "activo": True,
                },
            )
            tipo_objs[codigo] = tipo

        colaboradores = [
            ("CC", "1094881001", "Ana Maria", "Lopez", "Analista contable", "Financiera", "Sura EPS", "Positiva"),
            ("CC", "1002456789", "Miguel Angel", "Rios", "Auxiliar administrativo", "Gestion Humana", "Nueva EPS", "Sura ARL"),
            ("CC", "1112765432", "Sofia", "Martinez", "Coordinadora IPS", "Operaciones", "Sanitas", "Colmena"),
            ("CE", "78653210", "Julian", "Valencia", "Desarrollador", "Tecnologia", "Compensar", "Positiva"),
        ]
        colaborador_objs = []
        for tipo_doc, numero, nombres, apellidos, cargo, area, eps, arl in colaboradores:
            colaborador, _ = Colaborador.objects.update_or_create(
                numero_identificacion=numero,
                defaults={
                    "tipo_documento": tipo_doc,
                    "nombres": nombres,
                    "apellidos": apellidos,
                    "correo": f"{nombres.split()[0].lower()}.{apellidos.lower()}@empresa.local",
                    "telefono": "3001234567",
                    "cargo": cargo,
                    "area": area,
                    "eps": eps,
                    "arl": arl,
                    "activo": True,
                },
            )
            colaborador_objs.append(colaborador)

        registros = [
            (colaborador_objs[0], tipo_objs["EG"], "Sura EPS", date(2026, 4, 2), date(2026, 4, 5), Incapacidad.ESTADO_RECIBIDA),
            (colaborador_objs[1], tipo_objs["AL"], "Sura ARL", date(2026, 3, 18), date(2026, 3, 25), Incapacidad.ESTADO_TRANSCRITA),
            (colaborador_objs[2], tipo_objs["LM"], "Sanitas", date(2026, 2, 1), date(2026, 6, 6), Incapacidad.ESTADO_COBRADA),
            (colaborador_objs[3], tipo_objs["LP"], "Compensar", date(2026, 1, 10), date(2026, 1, 23), Incapacidad.ESTADO_PAGADA),
        ]
        for colaborador, tipo, entidad, inicio, fin, estado in registros:
            incapacidad, created = Incapacidad.objects.get_or_create(
                colaborador=colaborador,
                tipo=tipo,
                fecha_inicio=inicio,
                fecha_fin=fin,
                defaults={
                    "entidad_responsable": entidad,
                    "estado": estado,
                    "numero_radicado": f"RAD-{colaborador.numero_identificacion[-4:]}",
                    "creado_por": gh,
                    "actualizado_por": gh,
                    "observaciones": "Registro demo para pruebas academicas.",
                },
            )
            if created:
                soporte = ContentFile(b"%PDF-1.4\n% Soporte medico demo INCASOFT\n", name="soporte-demo.pdf")
                incapacidad.soporte_medico.save(f"soporte-{incapacidad.pk}.pdf", soporte, save=True)
                HistorialEstado.objects.create(
                    incapacidad=incapacidad,
                    estado_anterior=estado,
                    estado_nuevo=estado,
                    comentario="Registro demo inicial.",
                    usuario=gh,
                )

        self.stdout.write(self.style.SUCCESS("Datos demo creados. Usuarios: administrador, gestionhumana, gerente. Clave: IncaSoft2026*"))
